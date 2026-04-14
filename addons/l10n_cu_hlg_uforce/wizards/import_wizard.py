# -*- coding: utf-8 -*-
import logging
from datetime import datetime, date

from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.http import addons_manifest
import xml.dom.minidom

_logger = logging.getLogger('INFO')

resp_dic = {'nokey': _('You must request a registry key. Please contact the support center for a new one.'),
            'invalidkey': _('You are using a invalid key. Please contact the support center for a new one.'),
            'expkey': _('You are using a expired key. Please contact the support center for a new one.'),
            'invalidmod': _('You are using a invalid key. Please contact the support center for a new one.')}


class ImportHireDropWizard(models.TransientModel):
    _name = "l10n_cu_hlg_uforce.import_hire_drop_wizard"

    # def _get_default_connector(self):
    #     return self.env['db_external_connector.template'].search([('application', '=', 'fastos')], limit=1).id or False

    # connector_id = fields.Many2one('db_external_connector.template', 'Database', required=True,
    #                                default=_get_default_connector, domain=[('application', '=', 'fastos')])


    connector_id = fields.Many2one('db_external_connector.template', 'Database', required=True)

    @api.one
    def action_import(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        self.action_import_function()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('l10n_cu_hlg_uforce.menu_hire_drop_record').id},
        }

    @api.model
    def action_import_function(self):
        obj = self
        connector = self.connector_id
        if self._context.get('connector_id'):
            connector = self._context.get('connector_id')
            connection = self._context.get('connector_id').connect()
            obj = self.create({'connector_id': self._context.get('connector_id').id})
        else:
            if not self.connector_id:
                connector = self.env['db_external_connector.template'].search([('application', '=', 'fastos')], limit=1)
            connection = connector.connect()

        self.env['l10n_cu_hr_import.import_employee_wizard'].with_context(connector_id=connector).action_import_function()

        obj.import_hire_drop(connection)
        connection.close()

        # Updating degree_id from HR.Applicant
        # self.updateDegreeFromHrApplicant()

        return True

    @api.one
    def import_hire_drop(self, connection):
        # Updating supplement motives...
        self.import_supplement_motive(connection)

        # Updating gforza contract type
        self.import_contract_hr_type(connection)
        contract_hr_type_obj = self.env['l10n_cu_hlg_uforce.contract_hr_type']
        contract_hr_types = contract_hr_type_obj.search([])
        contract_hr_types_dict = {}
        for contract_hr_type in contract_hr_types:
            contract_hr_types_dict[contract_hr_type.external_id] = contract_hr_type.id

        # Updating hires and drop..
        cursor = connection.cursor()
        hire_drop_obj = self.env['l10n_cu_hlg_uforce.hire_drop_record']

        # hires
        try:
            cursor.execute("""Select top 1000 Id_Empleado, FechaAlta, Id_Contrato, Nombre, PrimerApellido, SegundoApellido FROM CPT_Empleados;""")
        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))
        active_employees = []
        for row in cursor:
            if row[0] not in active_employees:
                active_employees.append(row[0])
            employee = self.env['hr.employee'].search([('external_id', '=', row[0]), ('active', '=', True)], limit=1)
            hire = hire_drop_obj.search([('employee_id', '=', employee.id), ('record_date', '=', tools.ustr(row[1])),
                                         ('record_type', '=', 'hire')], limit=1)
            employee.write({
                'contract_hr_type_id': contract_hr_types_dict.get(row[2], False),
                'first_name': row[3],
                'last_name': row[4],
                'second_last_name': row[5]
            })
            if not hire.id:
                hire_data = {
                    'employee_id': employee.id,
                    'motive_id': self.env.ref('l10n_cu_hlg_uforce.supplement_motive_alta').id,
                    'name': employee.name,
                    'record_date': tools.ustr(row[1]),
                    'record_type': 'hire',
                    'company_id': employee.company_id.id
                }
                hire_drop_obj.create(hire_data)

        # drops
        department_obj = self.env['hr.department']
        departments = department_obj.search([])
        job_obj = self.env['hr.job']
        jobs = job_obj.search([])
        country = self.env['res.country'].search([('code', '=', 'CU')], limit=1)
        departments_dict = {}
        jobs_dict = {}
        for department in departments:
            departments_dict[department.external_id] = department
        for job in jobs:
            jobs_dict[job.external_id] = job.id

        try:
            cursor.execute("""SELECT id_Empleado, CI, Nombre + ' ' + PrimerApellido + ' ' + SegundoApellido AS nombre,
                                     FechaBaja, FechaAlta, CausaBaja, Sexo, Id_Area, Id_Departamento, Id_Cargo,                                     
                                     Id_CategOcupacional, Id_Contrato, Nombre, PrimerApellido, SegundoApellido
                              FROM dbo.CPT_HistoricoBajas;""")
            # , Direccion, Id_CausaBaja
        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))

        nd_motive = self.env.ref('l10n_cu_hlg_uforce.supplement_motive_null')

        for row in cursor:
            employee = self.env['hr.employee'].search(['|', ('external_id', '=', row[0]),
                                                       ('identification_id', '=', row[1])], limit=1)
            if not employee.id:
                employee = self.env['hr.employee'].search(['|', ('external_id', '=', row[0]),
                                                           ('identification_id', '=', row[1]), ('active', '=', False)],
                                                          limit=1)
                if not employee.id:
                    area = row[7] if row[7] is not None else ''
                    dpt = row[8] if row[8] is not None else ''
                    job = row[9] if row[9] is not None else ''
                    department = departments_dict.get(area + '-' + dpt, False)
                    employee_data = {
                        'external_id': tools.ustr(row[0]),
                        'identification_id': tools.ustr(row[1]),
                        'name': tools.ustr(row[2]),
                        'code': tools.ustr(row[0]),
                        'gender': 'female' if row[6] == 'F' else 'male',
                        'admission_date': row[4],
                        'country_id': country.id,
                        'department_id': department.id if department else False,
                        'job_id': jobs_dict.get(area + dpt + job, False),
                        'active': False,
                         #'contract_hr_type_id': contract_hr_types_dict.get(row[11], False),
                        'company_id': department.company_id.id if department and department.company_id.id else self.env.user.company_id.id

                    }
                    employee = self.env['hr.employee'].create(employee_data)
                # elif employee.external_id in active_employees:
                else:
                    employee.write({
                        # 'active': True,
                        #'contract_hr_type_id': contract_hr_types_dict.get(row[11], False),
                        'first_name': row[12],
                        'last_name': row[13],
                        'second_last_name': row[14]
                    })
            # elif employee.external_id not in active_employees:
            # else:
            #     employee.write({
            #         # 'active': False,
            #         'contract_hr_type_id': contract_hr_types_dict.get(row[11], False),
            #
            #     })

            drop = hire_drop_obj.search([('employee_id', '=', employee.id), ('record_date', '=', tools.ustr(row[3])),
                                         ('record_type', '=', 'drop')])
            hire = hire_drop_obj.search([('employee_id', '=', employee.id), ('record_date', '=', tools.ustr(row[4])),
                                         ('record_type', '=', 'hire')])

            if not drop.id:
                supplement_motive = self.env['hr_contract.supplement_motive'].search(
                    [('name', 'like', tools.ustr(row[5]) + '%')], limit=1).id or False
                drop_data = {
                    'employee_id': employee.id,
                    'motive_id': supplement_motive if supplement_motive else nd_motive.id,
                    'name': employee.name,
                    'record_date': tools.ustr(row[3]),
                    'record_type': 'drop',
                    'company_id': employee.company_id.id
                }
                hire_drop_obj.create(drop_data)

            if not hire.id:
                hire_data = {
                    'employee_id': employee.id,
                    'motive_id': self.env.ref('l10n_cu_hlg_uforce.supplement_motive_alta').id,
                    'name': employee.name,
                    'record_date': tools.ustr(row[4]),
                    'record_type': 'hire',
                    'company_id': employee.company_id.id
                }
                hire_drop_obj.create(hire_data)

        return True

    def import_supplement_motive(self, connection):
        supplement_obj = self.env['hr_contract.supplement_motive']
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT Id_CausaBaja, NombreCausaBaja FROM dbo.CPT_CausasBaja;""")
        except Exception, e:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))

        for row in cursor:
            supplement_data = {'name': tools.ustr(row[1]), 'code': tools.ustr(row[0])}
            supplement = supplement_obj.search([('code', '=', tools.ustr(row[0]))], limit=1)

            if len(supplement) == 0:
                supplement_obj.create(supplement_data)
            else:
                supplement.write(supplement_data)

        cursor.close()
        return True

    # update the degree_id from hr.applicant
    @api.multi
    def updateDegreeFromHrApplicant(self):
        employee_reg = self.env['hr.employee'].search([])

        # update from applicant
        for employee in employee_reg:
            if not employee.degree_id:
                applicant = self.env['hr.applicant'].search([('emp_id', '=', employee.id)], limit=1)
                if (applicant.degree_id):
                    employee.write({'degree_id': applicant.degree_id.id})

    def import_contract_hr_type(self, connection):
        contract_hr_type_obj = self.env['l10n_cu_hlg_uforce.contract_hr_type']
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT Id_Contrato, NombreContrato, Id_TipoContrato FROM CPT_Contratos;""")

        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                  and make sure to select the correct one..."""))

        for row in cursor:
            data = {'code': row[2], 'name': row[1], 'external_id': tools.ustr(row[0])}

            contract_hr_type = contract_hr_type_obj.search([('external_id', '=', tools.ustr(row[0]))], limit=1)

            if len(contract_hr_type) == 0:
                contract_hr_type_obj.create(data)
            else:
                contract_hr_type_obj.write(data)

        cursor.close()
        return True
