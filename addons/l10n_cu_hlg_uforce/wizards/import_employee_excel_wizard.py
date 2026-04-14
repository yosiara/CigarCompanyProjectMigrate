import base64
import os
import tempfile
from datetime import datetime

import xlrd
from odoo import models, api, fields, tools
from odoo.exceptions import ValidationError, _logger
from odoo.tools.translate import _

resp_dic = {'nokey': _('You must request a registry key. Please contact the support center for a new one.'),
            'invalidkey': _('You are using a invalid key. Please contact the support center for a new one.'),
            'expkey': _('You are using a expired key. Please contact the support center for a new one.'),
            'invalidmod': _('You are using a invalid key. Please contact the support center for a new one.')}


class ImportEmployeesExcel(models.TransientModel):
    _name = "l10n_cu_hlg_uforce.import_employee_excel_wizard"

    file_data = fields.Binary('Select template', required=True)
    file_name = fields.Char('File Name')

    def get_address(self, name, street, country_id, state, municipality):
        state_id = self.env['res.country.state'].search([('name', '=', state), ('country_id', '=', country_id)],
                                                        limit=1).id or None
        municipality_id = self.env['l10n_cu_base.municipality'].search([('name', '=', municipality),
                                                                        ('state_id', '=', state_id)],
                                                                       limit=1).id or None
        partner_data = {
            'name': name,
            'street': street,
            'country_id': country_id,
            'state_id': state_id,
            'municipality_id': municipality_id,
            'employee': False,  # la direccion del empleado no es un empleado
            'active': True
        }
        return self.env['res.partner'].create(partner_data)

    @api.multi
    def action_import_employee(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        file_path = tempfile.gettempdir() + '/file.xlsx'
        data = self.file_data
        f = open(file_path, 'wb')
        f.write(base64.decodestring(data))
        f.close()

        dir_excel = str(self.file_name).split('.')
        file_format = dir_excel[len(dir_excel) - 1]
        if file_format not in ('xls', 'xlsx'):
            raise ValidationError(_('Please, select the correct file!'))

        wb = xlrd.open_workbook(file_path)
        xl_sheet = wb.sheet_by_index(0)
        id_template = str(xl_sheet.cell(0, 0).value)
        if id_template != 'Odoo-GeForza-Employees':
            raise ValidationError(_('Please, select the correct employees template!'))

        xl_sheet_degree = wb.sheet_by_index(2)
        self.import_degree(xl_sheet=xl_sheet_degree)

        employee_obj = self.env['hr.employee']
        hire_drop_obj = self.env['l10n_cu_hlg_uforce.hire_drop_record']
        for row_idx in range(2, xl_sheet.nrows):
            employee_name = tools.ustr(xl_sheet.cell(row_idx, 0).value)
            employee_code = int(xl_sheet.cell(row_idx, 1).value)
            ci = int(xl_sheet.cell(row_idx, 2).value)
            birthday = datetime.strptime(tools.ustr(xl_sheet.cell(row_idx, 3).value), '%d-%m-%Y')
            gender = tools.ustr(xl_sheet.cell(row_idx, 4).value)
            admission_date = datetime.strptime(tools.ustr(xl_sheet.cell(row_idx, 5).value), '%d-%m-%Y')
            street = tools.ustr(xl_sheet.cell(row_idx, 6).value)
            municipality = tools.ustr(xl_sheet.cell(row_idx, 7).value)
            state = tools.ustr(xl_sheet.cell(row_idx, 8).value)
            department_name = tools.ustr(xl_sheet.cell(row_idx, 9).value)
            job = tools.ustr(xl_sheet.cell(row_idx, 10).value)
            job_code = tools.ustr(xl_sheet.cell(row_idx, 11).value)
            category = tools.ustr(xl_sheet.cell(row_idx, 12).value)
            category_code = tools.ustr(xl_sheet.cell(row_idx, 13).value)
            scale = tools.ustr(xl_sheet.cell(row_idx, 14).value)
            salary = float(xl_sheet.cell(row_idx, 15).value) if xl_sheet.cell(row_idx, 15).value != '' else 0.00
            school_level_code = int(xl_sheet.cell(row_idx, 16).value)if xl_sheet.cell(row_idx, 16).value != '' else 0.00
            degree_code = tools.ustr(xl_sheet.cell(row_idx, 17).value)
            country = self.env.ref('base.cu')

            salary_scale = self.import_salary_scale(name=scale)
            occupational_category = self.import_occupational_category(name=category, code=category_code)
            salary_group = self.import_salary_group(salary=salary, salary_scale_id=salary_scale.id,
                                                    occupational_category_id=occupational_category.id)
            school_level = self.env['l10n_cu_hlg_hr.employee_school_level'].search([('code', '=', school_level_code)],
                                                                                   limit=1)
            department = self.import_department(name=department_name)
            position = self.import_employee_position(name=job, salary_group_id=salary_group.id,
                                                     school_level_id=school_level.id, salary=salary)
            job = self.import_employee_job(name=job, code=job_code, position_id=position.id,
                                           department_id=department.id)
            address = self.get_address(name=employee_name, street=street, country_id=country.id,
                                       state=state, municipality=municipality)
            degree = self.env['l10n_cu_hlg_uforce.degree'].search([('code', '=', degree_code)], limit=1)

            employee_data = {
                'identification_id': ci,
                'name': employee_name,
                'code': employee_code,
                'gender': 'female' if gender == 'F' else 'male',
                'birthday': birthday,
                'admission_date': admission_date,
                'country_id': country.id,
                'department_id': department.id,
                'job_id': job.id,
                'school_level_id': school_level.id,
                'address_home_id': address.id,
                'degree_id': degree.id,
                'active': True
            }

            employee = employee_obj.search([('identification_id', '=', ci)], limit=1)

            if not employee.id:
                employee = employee_obj.search([('identification_id', '=', ci), ('active', '=', False)], limit=1)
                if not employee.id:
                    employee = employee_obj.create(employee_data)
                    _logger.info("Employee created: %s." % employee.name)
                else:
                    employee_data['active'] = True
                    employee.write(employee_data)
                    _logger.info("Employee updated: %s." % employee.name)
            else:
                employee.write(employee_data)
                _logger.info("Employee updated: %s." % employee.name)

        xl_sheet = wb.sheet_by_index(1)
        for row_idx in range(1, xl_sheet.nrows):
            employee_name = tools.ustr(xl_sheet.cell(row_idx, 0).value)
            ci = int(xl_sheet.cell(row_idx, 1).value)
            record_date = datetime.strptime(tools.ustr(xl_sheet.cell(row_idx, 2).value), '%d-%m-%Y')
            record_type = tools.ustr(xl_sheet.cell(row_idx, 3).value)
            motive_name = tools.ustr(xl_sheet.cell(row_idx, 4).value)
            motive_code = tools.ustr(xl_sheet.cell(row_idx, 5).value)

            if record_type.lower() == 'alta':
                motive = self.env.ref('l10n_cu_hlg_uforce.supplement_motive_alta')
                record_type = 'hire'
            else:
                motive = self.import_supplement_motive(name=motive_name, code=motive_code)
                record_type = 'drop'

            employee = employee_obj.search([('identification_id', '=', ci)], limit=1)
            if not employee.id:
                employee = employee_obj.search([('identification_id', '=', ci), ('active', '=', False)], limit=1)
                if not employee.id:
                    employee = employee_obj.create({'name': employee_name, 'identification_id': ci, 'active': False})
                    _logger.info("Employee created: %s." % employee.name)

            data = {
                'employee_id': employee.id,
                'motive_id': motive.id,
                'name': employee.name,
                'record_date': record_date,
                'record_type': record_type
            }

            hire_drop = hire_drop_obj.search([('employee_id', '=', employee.id), ('record_date', '=', record_date),
                                              ('record_type', '=', record_type)], limit=1)
            if not hire_drop.id:
                hire_drop_obj.create(data)
                _logger.info("Hire and Drop record created: %s." % employee.name)
            else:
                hire_drop.write(data)
                _logger.info("Hire and Drop record updated: %s." % employee.name)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('l10n_cu_hlg_uforce.uforce_employee_menu_item').id},
        }

    def import_occupational_category(self, name, code):
        occupational_category_obj = self.env['l10n_cu_hlg_hr.occupational_category']
        data = {'code': code, 'name': name}

        occupational_category = occupational_category_obj.search([('code', '=', code)], limit=1)

        if not occupational_category.id:
            order = occupational_category_obj.search([], order='order DESC', limit=1).order or 0
            data['order'] = int(order) + 1
            occupational_category = occupational_category_obj.create(data)
        else:
            occupational_category.write(data)

        return occupational_category

    def import_salary_scale(self, name):
        salary_scale_obj = self.env['l10n_cu_hlg_hr.salary_scale']
        data = {'name': name}
        salary_scale = salary_scale_obj.search([('name', '=', name)], limit=1)

        if not salary_scale.id:
            salary_scale = salary_scale_obj.create(data)
        else:
            salary_scale.write(data)

        return salary_scale

    def import_salary_group(self, salary, salary_scale_id, occupational_category_id):
        salary_group_obj = self.env['l10n_cu_hlg_hr.salary_group']

        data = {
            'scale_salary': salary,
            'salary_scale_id': salary_scale_id,
            'occupational_category_id': occupational_category_id,
        }

        salary_group = salary_group_obj.search([('scale_salary', '=', salary),
                                                ('occupational_category_id', '=', occupational_category_id)], limit=1)
        if not salary_group.id:
            salary_group = salary_group_obj.create(data)
        else:
            salary_group.write(data)

        return salary_group

    def import_employee_position(self, name, salary_group_id, school_level_id, salary):
        position_obj = self.env['l10n_cu_hlg_hr.position']
        data = {'name': name, 'salary_group_id': salary_group_id, 'school_level_id': school_level_id, 'salary': salary}

        position = position_obj.search([('name', '=', name), ('salary_group_id', '=', salary_group_id)], limit=1)
        if not position.id:
            position = position_obj.create(data)
        else:
            position.write(data)

        return position

    def import_department(self, name):
        department_obj = self.env['hr.department']
        department_data = {'name': name}

        department = department_obj.search([('name', '=', name)], limit=1)
        if not department.id:
            department = department_obj.create(department_data)
        else:
            department.write(department_data)
        return department

    def import_employee_job(self, name, code, position_id, department_id):
        job_obj = self.env['hr.job']
        data = {'name': name, 'code': code, 'position_id': position_id, 'department_id': department_id}

        job = job_obj.search([('name', '=', name), ('department_id', '=', department_id)], limit=1)
        if not job.id:
            job = job_obj.create(data)
        else:
            job.write(data)

        return job

    def import_supplement_motive(self, name, code):
        supplement_motive_obj = self.env['hr_contract.supplement_motive']
        supplement_motive_data = {'name': name, 'code': code}

        supplement_motive = supplement_motive_obj.search([('code', '=', code)], limit=1)
        if not supplement_motive.id:
            supplement_motive = supplement_motive_obj.create(supplement_motive_data)
        else:
            supplement_motive.write(supplement_motive_data)

        return supplement_motive

    def import_degree(self, xl_sheet=None):
        degree_obj = self.env['l10n_cu_hlg_uforce.degree']
        for row_idx in range(1, xl_sheet.nrows):
            code = str(xl_sheet.cell(row_idx, 0).value)
            code = code if str(code)[len(str(code)) - 2:] != '.0' else str(code)[0:len(str(code)) - 2]
            name = xl_sheet.cell(row_idx, 1).value
            parent_code = xl_sheet.cell(row_idx, 2).value
            parent_code = parent_code if str(parent_code)[len(str(parent_code)) - 2:] != '.0' else str(parent_code)[0:len(str(parent_code)) - 2]

            #search ids
            level_code = xl_sheet.cell(row_idx, 3).value
            level_code = level_code if str(level_code)[len(str(level_code)) - 2:] != '.0' else str(level_code)[0:len(str(level_code)) - 2]
            degree_level_id = self.env['l10n_cu_hlg_hr.employee_school_level'].search([('code','=',level_code)], limit=1).id

            branch_code = xl_sheet.cell(row_idx, 4).value
            branch_code = branch_code if str(branch_code)[len(str(branch_code)) - 2:] != '.0' else str(branch_code)[0:len(str(branch_code)) - 2]
            branch_science_id = self.env['l10n_cu_hlg_uforce.branch_science'].search([('code','=',branch_code)], limit=1).id

            specialty_family_code = xl_sheet.cell(row_idx, 5).value
            specialty_family_code = specialty_family_code if str(specialty_family_code)[len(str(specialty_family_code)) - 2:] != '.0' else str(specialty_family_code)[0:len(str(specialty_family_code)) - 2]
            specialty_family_id = self.env['l10n_cu_hlg_uforce.specialty_family'].search([('code', '=', specialty_family_code)],limit=1).id

            degree_data = {
                'name': name,
                'code': code,
                'parent_code': parent_code,
                'degree_level_id': degree_level_id,
                'branch_science_id': branch_science_id,
                'specialty_family_id': specialty_family_id
            }

            degree = degree_obj.search([('code', '=', code)], limit=1)
            if not degree.id:
                degree_obj.create(degree_data)
            else:
                degree.write(degree_data)

        # set the parent_id, match parent_code
        for degree in degree_obj.search([]):
            if degree.parent_code != '':
                degree_id = degree_obj.search([('code', '=', degree.parent_code)]).id
                degree.write({'parent_id': degree_id})
