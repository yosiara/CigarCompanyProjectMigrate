# -*- coding: utf-8 -*-
import os
import tempfile
import xlrd
import base64
import logging
from odoo import api, fields, models, tools
from dateutil.relativedelta import relativedelta
from odoo import models, api, fields
from odoo.fields import Selection, Binary, Char
from odoo.http import addons_manifest
from datetime import datetime
import xml.dom.minidom
from xml.dom import minidom
from tempfile import mktemp
from odoo.tools import ustr
from odoo.modules.module import get_module_path
from os.path import normpath, abspath
from lxml import etree
import xml.etree.ElementTree as ET
import re
from unicodedata import normalize
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime, date
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from xlwt import *
import xlsxwriter
from StringIO import StringIO
from ..reports import *
from odoo.tools.translate import _

_logger = logging.getLogger('INFO')

resp_dic = {'nokey': _('You must request a registry key. Please contact the support center for a new one.'),
            'invalidkey': _('You are using a invalid key. Please contact the support center for a new one.'),
            'expkey': _('You are using a expired key. Please contact the support center for a new one.'),
            'invalidmod': _('You are using a invalid key. Please contact the support center for a new one.')}


class UpdateFromGforza(models.TransientModel):
    _name = "l10n_cu_hlg_uforce.update_from_gforza_wizard"

    action_type = fields.Selection([('update', 'Update from GForza'),
                                    ('export', 'Export All Data in XML to Gforza')],
                                   string='Action to do', default='update')
    template = fields.Selection([('xml', 'XML')], string='XML files', default='xml')

    filename = Char()
    file = Binary(string='File to Import')

    filename_export = Char()
    file_export = Binary(string='File to Export')

    filename_xls_export = Char()
    file_xls_export = Binary(string='File to Export')

    demands = fields.Boolean(string='Demands Graduates', default=False, help='Demands Graduates Projection')
    employees = fields.Boolean(string='Employees Existence', default=False, help='Employee Existence')
    hire_drop = fields.Boolean(string='Hire and Drops', default=False, help='Drops Fluctuation')

    @api.onchange('action_type')
    def _onchange_action_type(self):
        self.file_export = None
        self.filename_export = None

    def _get_hire_date(self):
        list_dates = []
        check_list_dates = []
        for hd in self.env['l10n_cu_hlg_uforce.hire_drop_record'].search([('record_type', '=', 'hire')],
                                                                                order='record_date DESC'):
            if hd.employee_id.degree_id.id and hd.record_date not in check_list_dates:
                date_reg = (hd.record_date, hd.record_date)
                list_dates.append(date_reg)
                check_list_dates.append(hd.record_date)
        return list_dates

    # to string xml
    def tostring(self, element, declaration, encoding=None, method=None, ):
        class dummy:
            pass

        data = []
        data.append(declaration + "\n")
        file = dummy()
        file.write = data.append
        ET.ElementTree(element).write(file, encoding, method=method)
        return "".join(data)

    def del_acents(self, cad):
        trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
        cad = normalize('NFKC', normalize('NFKD', cad).translate(trans_tab))

        return cad

    def _save_file(self):
        file_name = mktemp(suffix='.xml')
        f = open(file_name, "wb")
        if self.file != None:
            f.write(base64.b64decode(self.file))
            f.close()
            return abspath(file_name)
        else:
            raise ValidationError(_("Error: you must select the XML file to import!!"))

    # function to return the text data from one node
    def getNodeText(self, node):
        nodeList = node.childNodes
        result = []
        for node in nodeList:
            if node.nodeType == node.TEXT_NODE:
                result.append(node.data)
        return ''.join(result)

    # function to return degree_id by code
    def getDegreeIdByCode(self, code):
        degree_id = self.env['l10n_cu_hlg_uforce.degree'].search([('code', '=', code)], limit=1).id
        return degree_id


    # function to validate CI
    def _check_identication_id(self, identification_id):
        if not identification_id or len(identification_id) != 11:
            return 4
        else:
            ci = str(identification_id)
            vci = identification_id
            cci = ''

            if int(vci[2:4]) < 1 or int(vci[2:4]) > 12:
                return 1
            if (int(vci[2:4]) == 1 or int(vci[2:4]) == 3 or int(vci[2:4]) == 5 or int(vci[2:4]) == 7 or int(
                    vci[2:4]) == 8 or int(vci[2:4]) == 10 or int(vci[2:4]) == 12) and (
                    int(vci[4:6]) < 1 or int(vci[4:6]) > 31):
                return 2
            if (int(vci[2:4]) == 4 or int(vci[2:4]) == 6 or int(vci[2:4]) == 9 or int(vci[2:4]) == 11) and (
                    int(vci[4:6]) < 1 or int(vci[4:6]) > 30):
                return 2
            if int(vci[2:4]) == 2 and int(vci[0:2]) % 4 == 0 and (int(vci[4:6]) < 1 or int(vci[4:6]) > 29):
                return 2
            if int(vci[2:4]) == 2 and int(vci[0:2]) % 4 != 0 and (int(vci[4:6]) < 1 or int(vci[4:6]) > 28):
                return 2
            else:
                # validate control digit
                sum = int(vci[0]) * 2 + int(vci[1]) * 1 + int(vci[2]) * 9 + int(vci[3]) * 8 + int(vci[4]) * 7 + int(
                    vci[5]) * 6 + int(vci[6]) * 5 + int(vci[7]) * 4 + int(vci[8]) * 3 + int(vci[9]) * 2
                rest = sum % 10

                if 10 - rest == 10:
                    cci = ci[0:10] + '0'
                else:
                    cci = ci[0:10] + str(10 - rest)

                if cci[10:11] != ci[10:11]:
                    return 3
                else:
                    return 0

    @api.multi
    def existBadCi(self):
        employees = self.env['hr.employee'].search([('degree_id', '!=', False)])

        for employee in employees:
            if self._check_identication_id(employee.identification_id) != 0:
                return True
        return False


    @api.multi
    def export_all(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        xmldoc = ET.Element("ModMatriz")
        xmldoc.set('Fecha', str(datetime.today().date()))

        xmldoc.set('Hora', str(datetime.today().hour) + ":" + str(datetime.today().minute))

        node_ocupados = ET.SubElement(xmldoc, "tb_sm_ocupados")

        employeeObj = self.env['hr.employee']

        sql_query = """select count(hr_employee.degree_id),l10n_cu_hlg_uforce_degree.code,l10n_cu_hlg_uforce_degree.id, l10n_cu_hlg_uforce_contract_hr_type.code,
                            l10n_cu_hlg_uforce_age_range.code,l10n_cu_hlg_uforce_age_range.id from hr_employee, l10n_cu_hlg_uforce_age_range,
                            l10n_cu_hlg_uforce_degree, l10n_cu_hlg_uforce_contract_hr_type
                            where l10n_cu_hlg_uforce_age_range.id = hr_employee.age_range_id and age != 0 and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id and
                            hr_employee.contract_hr_type_id = l10n_cu_hlg_uforce_contract_hr_type.id
                            group by hr_employee.degree_id, l10n_cu_hlg_uforce_age_range.code, l10n_cu_hlg_uforce_contract_hr_type.code, l10n_cu_hlg_uforce_degree.id,
                            l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_age_range.id order by l10n_cu_hlg_uforce_degree.code"""

        self.env.cr.execute(sql_query)
        ocupates = self.env.cr.fetchall()
        actual_year = datetime.today().year
        ministry_code = self.env.user.company_id.partner_id.ministry_id.code
        entity_code = self.env.user.company_id.gforza_code
        municipality_code = self.env.user.company_id.partner_id.municipality_id.external_id
        state_code = self.env.user.company_id.partner_id.state_id.external_id

        if not ministry_code or not entity_code or not municipality_code or not state_code:
            raise ValidationError(_('Please, check the entity settings!'))

        for ocupate in ocupates:
            contract_type = ocupate[3]
            if contract_type == 'I':
                contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Indeterminado')], limit=1).code
            else:
                contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Determinado')], limit=1).code

            count = ocupate[0]
            degree_code = ocupate[1]
            age_range_code = ocupate[4]

            # code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do
            ocupate_code = ministry_code + entity_code + degree_code + str(municipality_code) + str(
                state_code) + age_range_code + contract_type_code + str(actual_year)

            node_datos = ET.SubElement(node_ocupados, "datos")

            item_ocupate_code = ET.SubElement(node_datos, "id_ocupados")
            item_ocupate_code.text = ocupate_code

            item_entity_code = ET.SubElement(node_datos, "id_codigo_entidad")
            item_entity_code.text = entity_code

            item_degree_code = ET.SubElement(node_datos, "id_cod_carrera")
            item_degree_code.text = degree_code

            item_municipality_code = ET.SubElement(node_datos, "id_municipio_ocupado")
            item_municipality_code.text = str(municipality_code)

            item_contract_code = ET.SubElement(node_datos, "id_tipo_plaza")
            item_contract_code.text = contract_type_code

            item_age_range_code = ET.SubElement(node_datos, "id_rango_edad")
            item_age_range_code.text = age_range_code

            item_count_graduates = ET.SubElement(node_datos, "cant_graduados")
            item_count_graduates.text = str(count)

            item_year = ET.SubElement(node_datos, "ano_realizacion")
            item_year.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the person
        node_person = ET.SubElement(xmldoc, "tb_ma_persona")

        employees = employeeObj.search([('degree_id', '!=', False)])
        # code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do + CI

        for employee in employees:
            employee_degree_code = employee.degree_id.code

            if employee_degree_code and self._check_identication_id(employee.identification_id) == 0:

                employee_age_range_code = employee.age_range_id.code
                employee_contract_type_code = employee.contract_hr_type_id.code

                if employee_contract_type_code == 'I':
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                            [('name', '=', 'Indeterminado')], limit=1).code
                else:
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                            [('name', '=', 'Determinado')], limit=1).code

                person_code = ministry_code + entity_code + employee_degree_code + str(municipality_code) + str(
                        state_code) + employee_age_range_code + employee_contract_type_code + str(
                        actual_year) + employee.identification_id

                node_datos = ET.SubElement(node_person, "datos")

                item_person_code = ET.SubElement(node_datos, "id_persona")
                item_person_code.text = person_code

                item_person_ci = ET.SubElement(node_datos, "id_carnetidentidad")
                item_person_ci.text = employee.identification_id

                item_per_nombre = ET.SubElement(node_datos, "per_nombre")
                item_per_nombre.text = employee.first_name

                item_seg_nombre = ET.SubElement(node_datos, "sdo_nombre")

                item_per_apellido = ET.SubElement(node_datos, "per_apellido")
                item_per_apellido.text = employee.last_name

                item_sdo_apellido = ET.SubElement(node_datos, "sdo_apellido")
                item_sdo_apellido.text = employee.second_last_name


                item_edad_persona = ET.SubElement(node_datos, "edad_persona")
                item_edad_persona.text = ustr(employee.age)

                sexo = ''
                if employee.gender == 'female':
                    sexo = 'F'
                else:
                    sexo = 'M'

                item_sexo_persona = ET.SubElement(node_datos, "sexo_persona")
                item_sexo_persona.text = sexo

        node_person_ocupada = ET.SubElement(xmldoc, "tb_sm_persona_ocupado")
        employees = employeeObj.search([('degree_id', '!=', False)])

        for employee in employees:
            employee_degree_code = employee.degree_id.code

            if employee_degree_code and self._check_identication_id(employee.identification_id) == 0:

                cargo_code = employee.occupational_category_id.code

                employee_age_range_code = employee.age_range_id.code

                employee_contract_type_code = employee.contract_hr_type_id.code

                if employee_contract_type_code == 'I':
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                            [('name', '=', 'Indeterminado')], limit=1).code
                else:
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                            [('name', '=', 'Determinado')], limit=1).code

                if cargo_code == 'TEC':
                    cargo_code = '2000'
                elif cargo_code == 'ADM':
                    cargo_code = '5000'
                elif cargo_code == 'OBR':
                    cargo_code = '1000'
                elif cargo_code == 'SER':
                    cargo_code = '3000'
                elif cargo_code == 'DIR':
                    cargo_code = '4000'
                else:
                    cargo_code = '1000'

                persona_ocupado_code = ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year) + employee.identification_id + ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year)

                node_datos = ET.SubElement(node_person_ocupada, "datos")

                item_id_persona_ocupado = ET.SubElement(node_datos, "id_persona_ocupado")
                item_id_persona_ocupado.text = persona_ocupado_code

                item_id_persona = ET.SubElement(node_datos, "id_persona")
                item_id_persona.text = ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year) + employee.identification_id

                item_id_ocupado = ET.SubElement(node_datos, "id_ocupado")
                item_id_ocupado.text = ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year)

                item_id_cargo = ET.SubElement(node_datos, "id_cargo")
                item_id_cargo.text = cargo_code

                item_fecha_alta = ET.SubElement(node_datos, "fecha_alta")
                fecha_alta = employee.admission_date
                fecha_alta = fecha_alta.split("-")
                fecha_alta = fecha_alta[2] + "-" + fecha_alta[1] + "-" + fecha_alta[0]
                item_fecha_alta.text = ustr(fecha_alta)

        node_fluctuacion = ET.SubElement(xmldoc, "tb_sm_fluctuacion")

        fluctuacion_sql_query = """select count(hr_employee.degree_id), l10n_cu_hlg_uforce_degree.code, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_hire_drop_record.record_date from hr_employee, l10n_cu_hlg_uforce_hire_drop_record, l10n_cu_hlg_uforce_degree,
                                                hr_contract_supplement_motive  where hr_employee.id = l10n_cu_hlg_uforce_hire_drop_record.employee_id and
                                                l10n_cu_hlg_uforce_hire_drop_record.record_type = 'drop' and hr_contract_supplement_motive.id = l10n_cu_hlg_uforce_hire_drop_record.motive_id and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id
                                                and hr_employee.degree_id is not null and l10n_cu_hlg_uforce_hire_drop_record.record_date >= %s group by degree_id, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_hire_drop_record.record_date
                                                """
        year_query = datetime.today().year
        date_query = str(year_query) + '-01-01'

        self.env.cr.execute(fluctuacion_sql_query, (date_query,))
        fluctuates = self.env.cr.fetchall()

        for fluctuate in fluctuates:
            code_motive = ''
            if str(fluctuate[2]) == '1':
                code_motive = '1010'
            elif str(fluctuate[2]) == '2':
                code_motive = '1011'
            elif str(fluctuate[2]) == '3':
                code_motive = '1026'
            elif str(fluctuate[2]) == '4':
                code_motive = '1027'
            elif str(fluctuate[2]) == '5':
                code_motive = '1010'
            elif str(fluctuate[2]) == '6':
                code_motive = '1010'
            elif str(fluctuate[2]) == '7':
                code_motive = '1010'
            else:
                code_motive = '1010'

            fluctuacion_code = entity_code + str(municipality_code) + code_motive + str(fluctuate[1]) + str(
                actual_year)
            node_datos = ET.SubElement(node_fluctuacion, "datos")

            item_id_fluctuacion = ET.SubElement(node_datos, "id_fluctuacion")
            item_id_fluctuacion.text = fluctuacion_code

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            item_id_causal = ET.SubElement(node_datos, "id_causal")
            item_id_causal.text = code_motive

            item_id_carrera = ET.SubElement(node_datos, "id_carrera")
            item_id_carrera.text = fluctuate[1]

            item_cantidad = ET.SubElement(node_datos, "cantidad")
            item_cantidad.text = str(fluctuate[0])

            item_year = ET.SubElement(node_datos, "anno_realizacion")
            item_year.text = str(actual_year)

            item_otra = ET.SubElement(node_datos, "otra")

        node_persona_fluctuacion = ET.SubElement(xmldoc, "tb_sm_persona_fluctuacion")

        fluctuacion_persona_sql_query = """select hr_employee.identification_id, hr_employee.degree_id, l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_age_range.code, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_hire_drop_record.record_date, l10n_cu_hlg_uforce_contract_hr_type.code, hr_employee.occupational_category_id from hr_employee, l10n_cu_hlg_uforce_hire_drop_record, l10n_cu_hlg_uforce_degree,
                                                hr_contract_supplement_motive, l10n_cu_hlg_uforce_age_range, l10n_cu_hlg_uforce_contract_hr_type   where hr_employee.id = l10n_cu_hlg_uforce_hire_drop_record.employee_id and l10n_cu_hlg_uforce_age_range.id = hr_employee.age_range_id and
                                                l10n_cu_hlg_uforce_hire_drop_record.record_type = 'drop' and hr_contract_supplement_motive.id = l10n_cu_hlg_uforce_hire_drop_record.motive_id and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id and hr_employee.contract_hr_type_id = l10n_cu_hlg_uforce_contract_hr_type.id
                                                and hr_employee.degree_id is not null and l10n_cu_hlg_uforce_hire_drop_record.record_date >= %s """

        self.env.cr.execute(fluctuacion_persona_sql_query, (date_query,))
        fluctuates_person = self.env.cr.fetchall()

        for fluctuate_person in fluctuates_person:
            node_datos = ET.SubElement(node_persona_fluctuacion, "datos")

            code_motive = ''
            if fluctuate_person[4] == '1':
                code_motive = '1010'
            elif fluctuate_person[4] == '2':
                code_motive = '1011'
            elif fluctuate_person[4] == '3':
                code_motive = '1026'
            elif fluctuate_person[4] == '4':
                code_motive = '1027'
            elif fluctuate_person[4] == '5':
                code_motive = '1010'
            elif fluctuate_person[4] == '6':
                code_motive = '1010'
            elif fluctuate_person[4] == '7':
                code_motive = '1010'
            else:
                code_motive = '1010'

            cargo_code = self.env['l10n_cu_hlg_hr.occupational_category'].search([('id', '=', fluctuate_person[7])],
                                                                                 limit=1).code

            if cargo_code == 'TEC':
                cargo_code = '2000'
            elif cargo_code == 'ADM':
                cargo_code = '5000'
            elif cargo_code == 'OBR':
                cargo_code = '1000'
            elif cargo_code == 'SER':
                cargo_code = '3000'
            elif cargo_code == 'DIR':
                cargo_code = '4000'
            else:
                cargo_code = '1000'

            contract_type = '3401'

            if fluctuate_person[6] == 'I':
                contract_type = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Indeterminado')], limit=1).code
            else:
                contract_type = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Determinado')], limit=1).code

            persona_fluctuacion_code = ministry_code + entity_code + fluctuate_person[2] + str(municipality_code) + str(state_code) + \
                                       fluctuate_person[3] + contract_type + str(actual_year) + fluctuate_person[
                                           0] + entity_code + str(municipality_code) + code_motive + fluctuate_person[
                                           2] + str(actual_year)

            item_id_persona_fluctuacion = ET.SubElement(node_datos, "id_persona_fluctuacion")
            item_id_persona_fluctuacion.text = persona_fluctuacion_code

            item_id_persona = ET.SubElement(node_datos, "id_persona")
            item_id_persona.text = ministry_code + entity_code + fluctuate_person[2] + str(municipality_code) + str(state_code) + \
                                   fluctuate_person[3] + contract_type + str(actual_year) + fluctuate_person[0]

            item_id_fluctuacion = ET.SubElement(node_datos, "id_fluctuacion")
            item_id_fluctuacion.text = entity_code + str(municipality_code) + code_motive + fluctuate_person[2] + str(
                actual_year)

            item_id_cargo = ET.SubElement(node_datos, "id_cargo")
            item_id_cargo.text = cargo_code

            item_fecha_baja = ET.SubElement(node_datos, "fecha_baja")
            item_fecha_baja.text = fluctuate_person[5]

        # the demands and demands lines
        node_demanda_graduados = ET.SubElement(xmldoc, "tb_sm_demanda_graduados")

        demand_graduates = self.env['l10n_cu_hlg_uforce.graduates_demand'].search([])

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_demanda_graduados, "datos")
            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = demand_graduate.code_ftc3

            codeEntity = self.env.user.company_id.partner_id.gforza_code
            codeEntityMunicipality = self.env.user.municipality_id.external_id
            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = codeEntity
            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(codeEntityMunicipality)
            codeDegree = self.env['l10n_cu_hlg_uforce.degree'].search(
                [('id', '=', demand_graduate.degree_id.id)], limit=1).code

            item_id_carrera_demandada = ET.SubElement(node_datos, "id_carrera_demandada")
            item_id_carrera_demandada.text = codeDegree

            item_ano_realizacion = ET.SubElement(node_datos, "ano_realizacion")
            item_ano_realizacion.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

            node_datos = ET.SubElement(node_demanda_graduados, "datos")

            # FOR FTC4
            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = demand_graduate.code_ftc4

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = codeEntity

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(codeEntityMunicipality)

            codeDegree = self.env['l10n_cu_hlg_uforce.degree'].search(
                [('id', '=', demand_graduate.degree_id.id)], limit=1).code

            item_id_carrera_demandada = ET.SubElement(node_datos, "id_carrera_demandada")
            item_id_carrera_demandada.text = codeDegree

            item_ano_realizacion = ET.SubElement(node_datos, "ano_realizacion")
            item_ano_realizacion.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the demands line ftc3
        node_ftc3 = ET.SubElement(xmldoc, "tb_sm_modelo_ftc3")

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_ftc3, "datos")
            code_demanda_carrera = demand_graduate.code_ftc3

            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = code_demanda_carrera
            # search the period
            period_one_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 1))], limit=1).id
            demand_ftc3_one_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_one_id)], limit=1).quantity
            item_ano_mas_uno = ET.SubElement(node_datos, "ano_mas_uno")
            item_ano_mas_uno.text = str(demand_ftc3_one_quantity)

            period_two_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 2))], limit=1).id
            demand_ftc3_two_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_two_id)], limit=1).quantity
            item_ano_mas_dos = ET.SubElement(node_datos, "ano_mas_dos")
            item_ano_mas_dos.text = str(demand_ftc3_two_quantity)

            period_three_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 3))],
                                                                       limit=1).id
            demand_ftc3_three_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_three_id)], limit=1).quantity
            item_ano_mas_tres = ET.SubElement(node_datos, "ano_mas_tres")
            item_ano_mas_tres.text = str(demand_ftc3_three_quantity)

            period_four_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 4))], limit=1).id
            demand_ftc3_four_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_four_id)], limit=1).quantity
            item_ano_mas_cuatro = ET.SubElement(node_datos, "ano_mas_cuatro")
            item_ano_mas_cuatro.text = str(demand_ftc3_four_quantity)

            period_five_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 5))], limit=1).id
            demand_ftc3_five_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_five_id)], limit=1).quantity
            item_ano_mas_cinco = ET.SubElement(node_datos, "ano_mas_cinco")
            item_ano_mas_cinco.text = str(demand_ftc3_four_quantity)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the demands line ftc4
        node_ftc4 = ET.SubElement(xmldoc, "tb_sm_modelo_ftc4")

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_ftc4, "datos")
            code_demanda_carrera = demand_graduate.code_ftc4

            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = code_demanda_carrera
            # search the period
            period_six_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 1))], limit=1).id
            demand_ftc3_six_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_six_id)], limit=1).quantity
            item_ano_mas_seis = ET.SubElement(node_datos, "ano_mas_seis")
            item_ano_mas_seis.text = str(demand_ftc3_six_quantity)

            period_seven_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 2))],
                                                                       limit=1).id
            demand_ftc3_seven_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_seven_id)], limit=1).quantity
            item_ano_mas_siete = ET.SubElement(node_datos, "ano_mas_siete")
            item_ano_mas_siete.text = str(demand_ftc3_seven_quantity)

            period_eigth_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 3))],
                                                                       limit=1).id
            demand_ftc3_eigth_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_eigth_id)], limit=1).quantity
            item_ano_mas_ocho = ET.SubElement(node_datos, "ano_mas_ocho")
            item_ano_mas_ocho.text = str(demand_ftc3_eigth_quantity)

            period_nine_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 4))], limit=1).id
            demand_ftc3_nine_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_nine_id)], limit=1).quantity
            item_ano_mas_nueve = ET.SubElement(node_datos, "ano_mas_nueve")
            item_ano_mas_nueve.text = str(demand_ftc3_nine_quantity)

            period_ten_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 5))], limit=1).id
            demand_ftc3_ten_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_ten_id)], limit=1).quantity
            item_ano_mas_diez = ET.SubElement(node_datos, "ano_mas_diez")
            item_ano_mas_diez.text = str(demand_ftc3_ten_quantity)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        return xmldoc

    @api.multi
    def export_employees(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        xmldoc = ET.Element("ModMatriz")
        xmldoc.set('Fecha', str(datetime.today().date()))
        xmldoc.set('Hora', str(datetime.today().hour) + ":" + str(datetime.today().minute))

        node_ocupados = ET.SubElement(xmldoc, "tb_sm_ocupados")

        employeeObj = self.env['hr.employee']

        sql_query = """select count(hr_employee.degree_id),l10n_cu_hlg_uforce_degree.code,l10n_cu_hlg_uforce_degree.id, l10n_cu_hlg_uforce_contract_hr_type.code,
                            l10n_cu_hlg_uforce_age_range.code,l10n_cu_hlg_uforce_age_range.id from hr_employee, l10n_cu_hlg_uforce_age_range,
                            l10n_cu_hlg_uforce_degree, l10n_cu_hlg_uforce_contract_hr_type
                            where l10n_cu_hlg_uforce_age_range.id = hr_employee.age_range_id and age != 0 and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id and
                            hr_employee.contract_hr_type_id = l10n_cu_hlg_uforce_contract_hr_type.id
                            group by hr_employee.degree_id, l10n_cu_hlg_uforce_age_range.code, l10n_cu_hlg_uforce_contract_hr_type.code, l10n_cu_hlg_uforce_degree.id,
                            l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_age_range.id order by l10n_cu_hlg_uforce_degree.code"""

        self.env.cr.execute(sql_query)
        ocupates = self.env.cr.fetchall()
        actual_year = datetime.today().year

        entity_code = self.env.user.company_id.gforza_code
        municipality_code = self.env.user.company_id.partner_id.municipality_id.external_id
        ministry_code = self.env.user.company_id.organism_id.ministry_id.code
        state_code = self.env.user.company_id.partner_id.state_id.external_id

        if not ministry_code or not entity_code or not municipality_code or not state_code:
            raise ValidationError(_('Please, check the entity settings!'))

        for ocupate in ocupates:
            contract_type = ocupate[3]
            if contract_type == 'I':
                contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Indeterminado')], limit=1).code
            else:
                contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Determinado')], limit=1).code

            count = ocupate[0]
            degree_code = ocupate[1]
            age_range_code = ocupate[4]

            if not ministry_code or not entity_code or not municipality_code or not state_code:
                raise ValidationError(_('Please, check the entity settings!'))

            # code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do
            ocupate_code = ministry_code + entity_code + degree_code + str(municipality_code) + str(
                state_code) + age_range_code + contract_type_code + str(actual_year)

            node_datos = ET.SubElement(node_ocupados, "datos")

            item_ocupate_code = ET.SubElement(node_datos, "id_ocupados")
            item_ocupate_code.text = ocupate_code

            item_entity_code = ET.SubElement(node_datos, "id_codigo_entidad")
            item_entity_code.text = entity_code

            item_degree_code = ET.SubElement(node_datos, "id_cod_carrera")
            item_degree_code.text = degree_code

            item_municipality_code = ET.SubElement(node_datos, "id_municipio_ocupado")
            item_municipality_code.text = str(municipality_code)

            item_contract_code = ET.SubElement(node_datos, "id_tipo_plaza")
            item_contract_code.text = contract_type_code

            item_age_range_code = ET.SubElement(node_datos, "id_rango_edad")
            item_age_range_code.text = age_range_code

            item_count_graduates = ET.SubElement(node_datos, "cant_graduados")
            item_count_graduates.text = str(count)

            item_year = ET.SubElement(node_datos, "ano_realizacion")
            item_year.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the person
        node_person = ET.SubElement(xmldoc, "tb_ma_persona")

        employees = employeeObj.search([('degree_id', '!=', False)])
        # code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do + CI

        for employee in employees:
            employee_degree_code = employee.degree_id.code

            if employee_degree_code and self._check_identication_id(employee.identification_id) == 0:

                employee_age_range_code = employee.age_range_id.code
                employee_contract_type_code = employee.contract_hr_type_id.code

                if employee_contract_type_code == 'I':
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                        [('name', '=', 'Indeterminado')], limit=1).code
                else:
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                        [('name', '=', 'Determinado')], limit=1).code

                person_code = ministry_code + entity_code + employee_degree_code + str(municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year) + employee.identification_id

                node_datos = ET.SubElement(node_person, "datos")

                item_person_code = ET.SubElement(node_datos, "id_persona")
                item_person_code.text = person_code

                item_person_ci = ET.SubElement(node_datos, "id_carnetidentidad")
                item_person_ci.text = employee.identification_id

                item_per_nombre = ET.SubElement(node_datos, "per_nombre")
                item_per_nombre.text = employee.first_name

                item_seg_nombre = ET.SubElement(node_datos, "sdo_nombre")

                item_per_apellido = ET.SubElement(node_datos, "per_apellido")
                item_per_apellido.text = employee.last_name

                item_sdo_apellido = ET.SubElement(node_datos, "sdo_apellido")
                item_sdo_apellido.text = employee.second_last_name

                item_edad_persona = ET.SubElement(node_datos, "edad_persona")
                item_edad_persona.text = ustr(employee.age)



                sexo = ''
                if employee.gender == 'female':
                    sexo = 'F'
                else:
                    sexo = 'M'

                item_sexo_persona = ET.SubElement(node_datos, "sexo_persona")
                item_sexo_persona.text = sexo

        node_person_ocupada = ET.SubElement(xmldoc, "tb_sm_persona_ocupado")
        employees = employeeObj.search([('degree_id', '!=', False)])

        for employee in employees:
            employee_degree_code = employee.degree_id.code

            if employee_degree_code and self._check_identication_id(employee.identification_id) == 0:

                cargo_code =  employee.occupational_category_id.code

                employee_age_range_code = employee.age_range_id.code

                employee_contract_type_code = employee.contract_hr_type_id.code

                if employee_contract_type_code == 'I':
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                        [('name', '=', 'Indeterminado')], limit=1).code
                else:
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                        [('name', '=', 'Determinado')], limit=1).code

                if cargo_code == 'TEC':
                    cargo_code = '2000'
                elif cargo_code == 'ADM':
                    cargo_code = '5000'
                elif cargo_code == 'OBR':
                    cargo_code = '1000'
                elif cargo_code == 'SER':
                    cargo_code = '3000'
                elif cargo_code == 'DIR':
                    cargo_code = '4000'
                else:
                    cargo_code = '1000'

                persona_ocupado_code = ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year) + employee.identification_id + ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year)

                node_datos = ET.SubElement(node_person_ocupada, "datos")

                item_id_persona_ocupado = ET.SubElement(node_datos, "id_persona_ocupado")
                item_id_persona_ocupado.text = persona_ocupado_code

                item_id_persona = ET.SubElement(node_datos, "id_persona")
                item_id_persona.text = ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year) + employee.identification_id

                item_id_ocupado = ET.SubElement(node_datos, "id_ocupado")
                item_id_ocupado.text = ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year)

                item_id_cargo = ET.SubElement(node_datos, "id_cargo")
                item_id_cargo.text = cargo_code

                item_fecha_alta = ET.SubElement(node_datos, "fecha_alta")
                fecha_alta = employee.admission_date
                fecha_alta = fecha_alta.split("-")
                fecha_alta = fecha_alta[2] + "-" + fecha_alta[1] + "-" + fecha_alta[0]
                item_fecha_alta.text = ustr(fecha_alta)

        return xmldoc

    @api.multi
    def export_demands(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        xmldoc = ET.Element("ModMatriz")
        xmldoc.set('Fecha', str(datetime.today().date()))
        xmldoc.set('Hora', str(datetime.today().hour) + ":" + str(datetime.today().minute))
        actual_year = datetime.today().year

        entity_code = self.env.user.company_id.gforza_code
        municipality_code = self.env.user.company_id.partner_id.municipality_id.external_id
        node_demanda_graduados = ET.SubElement(xmldoc, "tb_sm_demanda_graduados")

        if not entity_code or not municipality_code:
            raise ValidationError(_('Please, check the entity settings!'))

        demand_graduates = self.env['l10n_cu_hlg_uforce.graduates_demand'].search([])

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_demanda_graduados, "datos")
            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = demand_graduate.code_ftc3

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            codeDegree = self.env['l10n_cu_hlg_uforce.degree'].search(
                [('id', '=', demand_graduate.degree_id.id)], limit=1).code

            item_id_carrera_demandada = ET.SubElement(node_datos, "id_carrera_demandada")
            item_id_carrera_demandada.text = codeDegree

            item_ano_realizacion = ET.SubElement(node_datos, "ano_realizacion")
            item_ano_realizacion.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

            node_datos = ET.SubElement(node_demanda_graduados, "datos")

            # FOR FTC4
            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = demand_graduate.code_ftc4

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            codeDegree = self.env['l10n_cu_hlg_uforce.degree'].search(
                [('id', '=', demand_graduate.degree_id.id)], limit=1).code

            item_id_carrera_demandada = ET.SubElement(node_datos, "id_carrera_demandada")
            item_id_carrera_demandada.text = codeDegree

            item_ano_realizacion = ET.SubElement(node_datos, "ano_realizacion")
            item_ano_realizacion.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the demands line ftc3
        node_ftc3 = ET.SubElement(xmldoc, "tb_sm_modelo_ftc3")

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_ftc3, "datos")
            code_demanda_carrera = demand_graduate.code_ftc3

            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = code_demanda_carrera
            # search the period
            period_one_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 1))], limit=1).id
            demand_ftc3_one_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_one_id)], limit=1).quantity
            item_ano_mas_uno = ET.SubElement(node_datos, "ano_mas_uno")
            item_ano_mas_uno.text = str(demand_ftc3_one_quantity)

            period_two_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 2))], limit=1).id
            demand_ftc3_two_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_two_id)], limit=1).quantity
            item_ano_mas_dos = ET.SubElement(node_datos, "ano_mas_dos")
            item_ano_mas_dos.text = str(demand_ftc3_two_quantity)

            period_three_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 3))],
                                                                       limit=1).id
            demand_ftc3_three_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_three_id)], limit=1).quantity
            item_ano_mas_tres = ET.SubElement(node_datos, "ano_mas_tres")
            item_ano_mas_tres.text = str(demand_ftc3_three_quantity)

            period_four_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 4))], limit=1).id
            demand_ftc3_four_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_four_id)], limit=1).quantity
            item_ano_mas_cuatro = ET.SubElement(node_datos, "ano_mas_cuatro")
            item_ano_mas_cuatro.text = str(demand_ftc3_four_quantity)

            period_five_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 5))], limit=1).id
            demand_ftc3_five_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_five_id)], limit=1).quantity
            item_ano_mas_cinco = ET.SubElement(node_datos, "ano_mas_cinco")
            item_ano_mas_cinco.text = str(demand_ftc3_four_quantity)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the demands line ftc4
        node_ftc4 = ET.SubElement(xmldoc, "tb_sm_modelo_ftc4")

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_ftc4, "datos")
            code_demanda_carrera = demand_graduate.code_ftc4

            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = code_demanda_carrera
            # search the period
            period_six_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 1))], limit=1).id
            demand_ftc3_six_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_six_id)], limit=1).quantity
            item_ano_mas_seis = ET.SubElement(node_datos, "ano_mas_seis")
            item_ano_mas_seis.text = str(demand_ftc3_six_quantity)

            period_seven_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 2))],
                                                                       limit=1).id
            demand_ftc3_seven_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_seven_id)], limit=1).quantity
            item_ano_mas_siete = ET.SubElement(node_datos, "ano_mas_siete")
            item_ano_mas_siete.text = str(demand_ftc3_seven_quantity)

            period_eigth_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 3))],
                                                                       limit=1).id
            demand_ftc3_eigth_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_eigth_id)], limit=1).quantity
            item_ano_mas_ocho = ET.SubElement(node_datos, "ano_mas_ocho")
            item_ano_mas_ocho.text = str(demand_ftc3_eigth_quantity)

            period_nine_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 4))], limit=1).id
            demand_ftc3_nine_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_nine_id)], limit=1).quantity
            item_ano_mas_nueve = ET.SubElement(node_datos, "ano_mas_nueve")
            item_ano_mas_nueve.text = str(demand_ftc3_nine_quantity)

            period_ten_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 5))], limit=1).id
            demand_ftc3_ten_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_ten_id)], limit=1).quantity
            item_ano_mas_diez = ET.SubElement(node_datos, "ano_mas_diez")
            item_ano_mas_diez.text = str(demand_ftc3_ten_quantity)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        return xmldoc

    @api.multi
    def export_hire_drop(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        xmldoc = ET.Element("ModMatriz")
        xmldoc.set('Fecha', str(datetime.today().date()))
        xmldoc.set('Hora', str(datetime.today().hour) + ":" + str(datetime.today().minute))
        actual_year = datetime.today().year

        ministry_code = self.env.user.company_id.partner_id.ministry_id.code
        entity_code = self.env.user.company_id.gforza_code
        municipality_code = self.env.user.company_id.partner_id.municipality_id.external_id
        state_code = self.env.user.company_id.partner_id.state_id.external_id

        if not ministry_code or not entity_code or not municipality_code or not state_code:
            raise ValidationError(_('Please, check the entity settings!'))

        node_fluctuacion = ET.SubElement(xmldoc, "tb_sm_fluctuacion")

        fluctuacion_sql_query = """select count(hr_employee.degree_id), l10n_cu_hlg_uforce_degree.code, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_hire_drop_record.record_date from hr_employee, l10n_cu_hlg_uforce_hire_drop_record, l10n_cu_hlg_uforce_degree,
                                        hr_contract_supplement_motive  where hr_employee.id = l10n_cu_hlg_uforce_hire_drop_record.employee_id and
                                        l10n_cu_hlg_uforce_hire_drop_record.record_type = 'drop' and hr_contract_supplement_motive.id = l10n_cu_hlg_uforce_hire_drop_record.motive_id and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id
                                        and hr_employee.degree_id is not null and l10n_cu_hlg_uforce_hire_drop_record.record_date >= %s group by degree_id, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_hire_drop_record.record_date
                                        """
        year_query = datetime.today().year
        date_query = str(year_query) + '-01-01'

        self.env.cr.execute(fluctuacion_sql_query, (date_query,))
        fluctuates = self.env.cr.fetchall()

        for fluctuate in fluctuates:
            code_motive = ''
            if str(fluctuate[2]) == '1':
                code_motive = '1010'
            elif str(fluctuate[2]) == '2':
                code_motive = '1011'
            elif str(fluctuate[2]) == '3':
                code_motive = '1026'
            elif str(fluctuate[2]) == '4':
                code_motive = '1027'
            elif str(fluctuate[2]) == '5':
                code_motive = '1010'
            elif str(fluctuate[2]) == '6':
                code_motive = '1010'
            elif str(fluctuate[2]) == '7':
                code_motive = '1010'
            else:
                code_motive = '1010'

            fluctuacion_code = entity_code + str(municipality_code) + code_motive + str(fluctuate[1]) + str(actual_year)
            node_datos = ET.SubElement(node_fluctuacion, "datos")

            item_id_fluctuacion = ET.SubElement(node_datos, "id_fluctuacion")
            item_id_fluctuacion.text = fluctuacion_code

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            item_id_causal = ET.SubElement(node_datos, "id_causal")
            item_id_causal.text = code_motive

            item_id_carrera = ET.SubElement(node_datos, "id_carrera")
            item_id_carrera.text = fluctuate[1]

            item_cantidad = ET.SubElement(node_datos, "cantidad")
            item_cantidad.text = str(fluctuate[0])

            item_year = ET.SubElement(node_datos, "anno_realizacion")
            item_year.text = str(actual_year)

            item_otra = ET.SubElement(node_datos, "otra")

        node_persona_fluctuacion = ET.SubElement(xmldoc, "tb_sm_persona_fluctuacion")

        fluctuacion_persona_sql_query = """select hr_employee.identification_id, hr_employee.degree_id, l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_age_range.code, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_hire_drop_record.record_date, l10n_cu_hlg_uforce_contract_hr_type.code, hr_employee.occupational_category_id from hr_employee, l10n_cu_hlg_uforce_hire_drop_record, l10n_cu_hlg_uforce_degree,
                                        hr_contract_supplement_motive, l10n_cu_hlg_uforce_age_range, l10n_cu_hlg_uforce_contract_hr_type   where hr_employee.id = l10n_cu_hlg_uforce_hire_drop_record.employee_id and l10n_cu_hlg_uforce_age_range.id = hr_employee.age_range_id and
                                        l10n_cu_hlg_uforce_hire_drop_record.record_type = 'drop' and hr_contract_supplement_motive.id = l10n_cu_hlg_uforce_hire_drop_record.motive_id and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id and hr_employee.contract_hr_type_id = l10n_cu_hlg_uforce_contract_hr_type.id
                                        and hr_employee.degree_id is not null and l10n_cu_hlg_uforce_hire_drop_record.record_date >= %s """

        self.env.cr.execute(fluctuacion_persona_sql_query, (date_query,))
        fluctuates_person = self.env.cr.fetchall()

        for fluctuate_person in fluctuates_person:
            node_datos = ET.SubElement(node_persona_fluctuacion, "datos")

            code_motive = ''
            if fluctuate_person[4] == '1':
                code_motive = '1010'
            elif fluctuate_person[4] == '2':
                code_motive = '1011'
            elif fluctuate_person[4] == '3':
                code_motive = '1026'
            elif fluctuate_person[4] == '4':
                code_motive = '1027'
            elif fluctuate_person[4] == '5':
                code_motive = '1010'
            elif fluctuate_person[4] == '6':
                code_motive = '1010'
            elif fluctuate_person[4] == '7':
                code_motive = '1010'
            else:
                code_motive = '1010'

            cargo_code = self.env['l10n_cu_hlg_hr.occupational_category'].search([('id', '=', fluctuate_person[7])],
                                                                                 limit=1).code

            if cargo_code == 'TEC':
                cargo_code = '2000'
            elif cargo_code == 'ADM':
                cargo_code = '5000'
            elif cargo_code == 'OBR':
                cargo_code = '1000'
            elif cargo_code == 'SER':
                cargo_code = '3000'
            elif cargo_code == 'DIR':
                cargo_code = '4000'
            else:
                cargo_code = '1000'

            contract_type = '3401'

            if fluctuate_person[6] == 'I':
                contract_type = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Indeterminado')], limit=1).code
            else:
                contract_type = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Determinado')], limit=1).code

            persona_fluctuacion_code = ministry_code + entity_code + fluctuate_person[2] + str(municipality_code) + str(state_code) + \
                                       fluctuate_person[3] + contract_type + str(actual_year) + fluctuate_person[
                                           0] + entity_code + str(municipality_code) + code_motive + fluctuate_person[
                                           2] + str(actual_year)

            item_id_persona_fluctuacion = ET.SubElement(node_datos, "id_persona_fluctuacion")
            item_id_persona_fluctuacion.text = persona_fluctuacion_code

            item_id_persona = ET.SubElement(node_datos, "id_persona")
            item_id_persona.text = ministry_code + entity_code + fluctuate_person[2] + str(municipality_code) + str(state_code) + \
                                   fluctuate_person[3] + contract_type + str(actual_year) + fluctuate_person[0]

            item_id_fluctuacion = ET.SubElement(node_datos, "id_fluctuacion")
            item_id_fluctuacion.text = entity_code + str(municipality_code) + code_motive + fluctuate_person[2] + str(
                actual_year)

            item_id_cargo = ET.SubElement(node_datos, "id_cargo")
            item_id_cargo.text = cargo_code

            item_fecha_baja = ET.SubElement(node_datos, "fecha_baja")
            item_fecha_baja.text = fluctuate_person[5]

        return xmldoc

    @api.multi
    def export_employees_demands(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        xmldoc = ET.Element("ModMatriz")
        xmldoc.set('Fecha', str(datetime.today().date()))
        xmldoc.set('Hora', str(datetime.today().hour) + ":" + str(datetime.today().minute))

        node_ocupados = ET.SubElement(xmldoc, "tb_sm_ocupados")

        employeeObj = self.env['hr.employee']

        sql_query = """select count(hr_employee.degree_id),l10n_cu_hlg_uforce_degree.code,l10n_cu_hlg_uforce_degree.id, l10n_cu_hlg_uforce_contract_hr_type.code,
                            l10n_cu_hlg_uforce_age_range.code,l10n_cu_hlg_uforce_age_range.id from hr_employee, l10n_cu_hlg_uforce_age_range,
                            l10n_cu_hlg_uforce_degree, l10n_cu_hlg_uforce_contract_hr_type
                            where l10n_cu_hlg_uforce_age_range.id = hr_employee.age_range_id and age != 0 and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id and
                            hr_employee.contract_hr_type_id = l10n_cu_hlg_uforce_contract_hr_type.id
                            group by hr_employee.degree_id, l10n_cu_hlg_uforce_age_range.code, l10n_cu_hlg_uforce_contract_hr_type.code, l10n_cu_hlg_uforce_degree.id,
                            l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_age_range.id order by l10n_cu_hlg_uforce_degree.code"""

        self.env.cr.execute(sql_query)
        ocupates = self.env.cr.fetchall()
        actual_year = datetime.today().year

        entity_code = self.env.user.company_id.gforza_code
        municipality_code = self.env.user.company_id.partner_id.municipality_id.external_id
        ministry_code = self.env.user.company_id.organism_id.ministry_id.code
        state_code = self.env.user.company_id.partner_id.state_id.external_id

        if not ministry_code or not entity_code or not municipality_code or not state_code:
            raise ValidationError(_('Please, check the entity settings!'))

        for ocupate in ocupates:
            contract_type = ocupate[3]
            if contract_type == 'I':
                contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Indeterminado')], limit=1).code
            else:
                contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Determinado')], limit=1).code

            count = ocupate[0]
            degree_code = ocupate[1]
            age_range_code = ocupate[4]

            # code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do
            ocupate_code = ministry_code + entity_code + degree_code + str(municipality_code) + str(
                state_code) + age_range_code + contract_type_code + str(actual_year)

            node_datos = ET.SubElement(node_ocupados, "datos")

            item_ocupate_code = ET.SubElement(node_datos, "id_ocupados")
            item_ocupate_code.text = ocupate_code

            item_entity_code = ET.SubElement(node_datos, "id_codigo_entidad")
            item_entity_code.text = entity_code

            item_degree_code = ET.SubElement(node_datos, "id_cod_carrera")
            item_degree_code.text = degree_code

            item_municipality_code = ET.SubElement(node_datos, "id_municipio_ocupado")
            item_municipality_code.text = str(municipality_code)

            item_contract_code = ET.SubElement(node_datos, "id_tipo_plaza")
            item_contract_code.text = contract_type_code

            item_age_range_code = ET.SubElement(node_datos, "id_rango_edad")
            item_age_range_code.text = age_range_code

            item_count_graduates = ET.SubElement(node_datos, "cant_graduados")
            item_count_graduates.text = str(count)

            item_year = ET.SubElement(node_datos, "ano_realizacion")
            item_year.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the person
        node_person = ET.SubElement(xmldoc, "tb_ma_persona")

        employees = employeeObj.search([('degree_id', '!=', False)])
        # code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do + CI


        for employee in employees:
            employee_degree_code = employee.degree_id.code

            if employee_degree_code and self._check_identication_id(employee.identification_id) == 0:

                employee_age_range_code = employee.age_range_id.code
                employee_contract_type_code = employee.contract_hr_type_id.code

                if employee_contract_type_code == 'I':
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                            [('name', '=', 'Indeterminado')], limit=1).code
                else:
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                            [('name', '=', 'Determinado')], limit=1).code

                person_code = ministry_code + entity_code + employee_degree_code + str(municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year) + employee.identification_id

                node_datos = ET.SubElement(node_person, "datos")

                item_person_code = ET.SubElement(node_datos, "id_persona")
                item_person_code.text = person_code

                item_person_ci = ET.SubElement(node_datos, "id_carnetidentidad")
                item_person_ci.text = employee.identification_id

                item_per_nombre = ET.SubElement(node_datos, "per_nombre")

                item_per_nombre = ET.SubElement(node_datos, "per_nombre")
                item_per_nombre.text = employee.first_name

                item_seg_nombre = ET.SubElement(node_datos, "sdo_nombre")

                item_per_apellido = ET.SubElement(node_datos, "per_apellido")
                item_per_apellido.text = employee.last_name

                item_sdo_apellido = ET.SubElement(node_datos, "sdo_apellido")
                item_sdo_apellido.text = employee.second_last_name

                item_edad_persona = ET.SubElement(node_datos, "edad_persona")
                item_edad_persona.text = ustr(employee.age)

                sexo = ''
                if employee.gender == 'female':
                    sexo = 'F'
                else:
                    sexo = 'M'

                item_sexo_persona = ET.SubElement(node_datos, "sexo_persona")
                item_sexo_persona.text = sexo

        node_person_ocupada = ET.SubElement(xmldoc, "tb_sm_persona_ocupado")
        employees = employeeObj.search([('degree_id', '!=', False)])

        for employee in employees:
            employee_degree_code = employee.degree_id.code

            if employee_degree_code and self._check_identication_id(employee.identification_id) == 0:

                cargo_code = employee.occupational_category_id.code

                employee_age_range_code = employee.age_range_id.code

                employee_contract_type_code = employee.contract_hr_type_id.code

                if employee_contract_type_code == 'I':
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                        [('name', '=', 'Indeterminado')], limit=1).code
                else:
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                        [('name', '=', 'Determinado')], limit=1).code

                if cargo_code == 'TEC':
                    cargo_code = '2000'
                elif cargo_code == 'ADM':
                    cargo_code = '5000'
                elif cargo_code == 'OBR':
                    cargo_code = '1000'
                elif cargo_code == 'SER':
                    cargo_code = '3000'
                elif cargo_code == 'DIR':
                    cargo_code = '4000'
                else:
                    cargo_code = '1000'

                persona_ocupado_code = ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year) + employee.identification_id + ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year)

                node_datos = ET.SubElement(node_person_ocupada, "datos")

                item_id_persona_ocupado = ET.SubElement(node_datos, "id_persona_ocupado")
                item_id_persona_ocupado.text = persona_ocupado_code

                item_id_persona = ET.SubElement(node_datos, "id_persona")
                item_id_persona.text = ministry_code + entity_code + employee_degree_code + str(
                    municipality_code) + str(
                    state_code) + employee_age_range_code + employee_contract_type_code + str(
                    actual_year) + employee.identification_id

                item_id_ocupado = ET.SubElement(node_datos, "id_ocupado")
                item_id_ocupado.text = ministry_code + entity_code + employee_degree_code + str(
                        municipality_code) + str(
                        state_code) + employee_age_range_code + employee_contract_type_code + str(
                        actual_year)

                item_id_cargo = ET.SubElement(node_datos, "id_cargo")
                item_id_cargo.text = cargo_code

                item_fecha_alta = ET.SubElement(node_datos, "fecha_alta")
                fecha_alta = employee.admission_date
                fecha_alta = fecha_alta.split("-")
                fecha_alta = fecha_alta[2] + "-" + fecha_alta[1] + "-" + fecha_alta[0]
                item_fecha_alta.text = ustr(fecha_alta)


        node_demanda_graduados = ET.SubElement(xmldoc, "tb_sm_demanda_graduados")

        demand_graduates = self.env['l10n_cu_hlg_uforce.graduates_demand'].search([])

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_demanda_graduados, "datos")
            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = demand_graduate.code_ftc3

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code
            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)
            codeDegree = self.env['l10n_cu_hlg_uforce.degree'].search(
                [('id', '=', demand_graduate.degree_id.id)], limit=1).code

            item_id_carrera_demandada = ET.SubElement(node_datos, "id_carrera_demandada")
            item_id_carrera_demandada.text = codeDegree

            item_ano_realizacion = ET.SubElement(node_datos, "ano_realizacion")
            item_ano_realizacion.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

            node_datos = ET.SubElement(node_demanda_graduados, "datos")

            # FOR FTC4
            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = demand_graduate.code_ftc4

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            codeDegree = self.env['l10n_cu_hlg_uforce.degree'].search(
                [('id', '=', demand_graduate.degree_id.id)], limit=1).code

            item_id_carrera_demandada = ET.SubElement(node_datos, "id_carrera_demandada")
            item_id_carrera_demandada.text = codeDegree

            item_ano_realizacion = ET.SubElement(node_datos, "ano_realizacion")
            item_ano_realizacion.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the demands line ftc3
        node_ftc3 = ET.SubElement(xmldoc, "tb_sm_modelo_ftc3")

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_ftc3, "datos")
            code_demanda_carrera = demand_graduate.code_ftc3

            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = code_demanda_carrera
            # search the period
            period_one_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 1))], limit=1).id
            demand_ftc3_one_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_one_id)], limit=1).quantity
            item_ano_mas_uno = ET.SubElement(node_datos, "ano_mas_uno")
            item_ano_mas_uno.text = str(demand_ftc3_one_quantity)

            period_two_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 2))], limit=1).id
            demand_ftc3_two_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_two_id)], limit=1).quantity
            item_ano_mas_dos = ET.SubElement(node_datos, "ano_mas_dos")
            item_ano_mas_dos.text = str(demand_ftc3_two_quantity)

            period_three_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 3))],
                                                                       limit=1).id
            demand_ftc3_three_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_three_id)], limit=1).quantity
            item_ano_mas_tres = ET.SubElement(node_datos, "ano_mas_tres")
            item_ano_mas_tres.text = str(demand_ftc3_three_quantity)

            period_four_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 4))], limit=1).id
            demand_ftc3_four_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_four_id)], limit=1).quantity
            item_ano_mas_cuatro = ET.SubElement(node_datos, "ano_mas_cuatro")
            item_ano_mas_cuatro.text = str(demand_ftc3_four_quantity)

            period_five_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 5))], limit=1).id
            demand_ftc3_five_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_five_id)], limit=1).quantity
            item_ano_mas_cinco = ET.SubElement(node_datos, "ano_mas_cinco")
            item_ano_mas_cinco.text = str(demand_ftc3_four_quantity)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the demands line ftc4
        node_ftc4 = ET.SubElement(xmldoc, "tb_sm_modelo_ftc4")

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_ftc4, "datos")
            code_demanda_carrera = demand_graduate.code_ftc4

            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = code_demanda_carrera
            # search the period
            period_six_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 1))], limit=1).id
            demand_ftc3_six_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_six_id)], limit=1).quantity
            item_ano_mas_seis = ET.SubElement(node_datos, "ano_mas_seis")
            item_ano_mas_seis.text = str(demand_ftc3_six_quantity)

            period_seven_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 2))],
                                                                       limit=1).id
            demand_ftc3_seven_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_seven_id)], limit=1).quantity
            item_ano_mas_siete = ET.SubElement(node_datos, "ano_mas_siete")
            item_ano_mas_siete.text = str(demand_ftc3_seven_quantity)

            period_eigth_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 3))],
                                                                       limit=1).id
            demand_ftc3_eigth_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_eigth_id)], limit=1).quantity
            item_ano_mas_ocho = ET.SubElement(node_datos, "ano_mas_ocho")
            item_ano_mas_ocho.text = str(demand_ftc3_eigth_quantity)

            period_nine_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 4))], limit=1).id
            demand_ftc3_nine_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_nine_id)], limit=1).quantity
            item_ano_mas_nueve = ET.SubElement(node_datos, "ano_mas_nueve")
            item_ano_mas_nueve.text = str(demand_ftc3_nine_quantity)

            period_ten_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 5))], limit=1).id
            demand_ftc3_ten_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_ten_id)], limit=1).quantity
            item_ano_mas_diez = ET.SubElement(node_datos, "ano_mas_diez")
            item_ano_mas_diez.text = str(demand_ftc3_ten_quantity)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        return xmldoc

    @api.multi
    def export_employees_hire_drops(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        xmldoc = ET.Element("ModMatriz")
        xmldoc.set('Fecha', str(datetime.today().date()))
        xmldoc.set('Hora', str(datetime.today().hour) + ":" + str(datetime.today().minute))

        node_ocupados = ET.SubElement(xmldoc, "tb_sm_ocupados")

        employeeObj = self.env['hr.employee']

        sql_query = """select count(hr_employee.degree_id),l10n_cu_hlg_uforce_degree.code,l10n_cu_hlg_uforce_degree.id, l10n_cu_hlg_uforce_contract_hr_type.code,
                            l10n_cu_hlg_uforce_age_range.code,l10n_cu_hlg_uforce_age_range.id from hr_employee, l10n_cu_hlg_uforce_age_range,
                            l10n_cu_hlg_uforce_degree, l10n_cu_hlg_uforce_contract_hr_type
                            where l10n_cu_hlg_uforce_age_range.id = hr_employee.age_range_id and age != 0 and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id and
                            hr_employee.contract_hr_type_id = l10n_cu_hlg_uforce_contract_hr_type.id
                            group by hr_employee.degree_id, l10n_cu_hlg_uforce_age_range.code, l10n_cu_hlg_uforce_contract_hr_type.code, l10n_cu_hlg_uforce_degree.id,
                            l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_age_range.id order by l10n_cu_hlg_uforce_degree.code"""

        self.env.cr.execute(sql_query)
        ocupates = self.env.cr.fetchall()
        actual_year = datetime.today().year

        entity_code = self.env.user.company_id.gforza_code
        municipality_code = self.env.user.company_id.partner_id.municipality_id.external_id
        ministry_code = self.env.user.company_id.organism_id.ministry_id.code
        state_code = self.env.user.company_id.partner_id.state_id.external_id

        if not ministry_code or not entity_code or not municipality_code or not state_code:
            raise ValidationError(_('Please, check the entity settings!'))

        for ocupate in ocupates:
            contract_type = ocupate[3]
            if contract_type == 'I':
                contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Indeterminado')], limit=1).code
            else:
                contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Determinado')], limit=1).code

            count = ocupate[0]
            degree_code = ocupate[1]
            age_range_code = ocupate[4]

            # code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do
            ocupate_code = ministry_code + entity_code + degree_code + str(municipality_code) + str(
                state_code) + age_range_code + contract_type_code + str(actual_year)

            node_datos = ET.SubElement(node_ocupados, "datos")

            item_ocupate_code = ET.SubElement(node_datos, "id_ocupados")
            item_ocupate_code.text = ocupate_code

            item_entity_code = ET.SubElement(node_datos, "id_codigo_entidad")
            item_entity_code.text = entity_code

            item_degree_code = ET.SubElement(node_datos, "id_cod_carrera")
            item_degree_code.text = degree_code

            item_municipality_code = ET.SubElement(node_datos, "id_municipio_ocupado")
            item_municipality_code.text = str(municipality_code)

            item_contract_code = ET.SubElement(node_datos, "id_tipo_plaza")
            item_contract_code.text = contract_type_code

            item_age_range_code = ET.SubElement(node_datos, "id_rango_edad")
            item_age_range_code.text = age_range_code

            item_count_graduates = ET.SubElement(node_datos, "cant_graduados")
            item_count_graduates.text = str(count)

            item_year = ET.SubElement(node_datos, "ano_realizacion")
            item_year.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the person
        node_person = ET.SubElement(xmldoc, "tb_ma_persona")

        employees = employeeObj.search([('degree_id', '!=', False)])
        # code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do + CI

        for employee in employees:
            employee_degree_code = employee.degree_id.code

            if employee_degree_code and self._check_identication_id(employee.identification_id) == 0:

                employee_age_range_code = employee.age_range_id.code
                employee_contract_type_code = employee.contract_hr_type_id.code

                if employee_contract_type_code == 'I':
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                        [('name', '=', 'Indeterminado')], limit=1).code
                else:
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                        [('name', '=', 'Determinado')], limit=1).code

                person_code = ministry_code + entity_code + employee_degree_code + str(municipality_code) + str(
                        state_code) + employee_age_range_code + employee_contract_type_code + str(
                        actual_year) + employee.identification_id

                node_datos = ET.SubElement(node_person, "datos")

                item_person_code = ET.SubElement(node_datos, "id_persona")
                item_person_code.text = person_code

                item_person_ci = ET.SubElement(node_datos, "id_carnetidentidad")
                item_person_ci.text = employee.identification_id

                item_per_nombre = ET.SubElement(node_datos, "per_nombre")
                item_per_nombre = ET.SubElement(node_datos, "per_nombre")
                item_per_nombre.text = employee.first_name

                item_seg_nombre = ET.SubElement(node_datos, "sdo_nombre")

                item_per_apellido = ET.SubElement(node_datos, "per_apellido")
                item_per_apellido.text = employee.last_name

                item_sdo_apellido = ET.SubElement(node_datos, "sdo_apellido")
                item_sdo_apellido.text = employee.second_last_name

                item_edad_persona = ET.SubElement(node_datos, "edad_persona")
                item_edad_persona.text = ustr(employee.age)

                sexo = ''
                if employee.gender == 'female':
                    sexo = 'F'
                else:
                    sexo = 'M'

                item_sexo_persona = ET.SubElement(node_datos, "sexo_persona")
                item_sexo_persona.text = sexo

        node_person_ocupada = ET.SubElement(xmldoc, "tb_sm_persona_ocupado")
        employees = employeeObj.search([('degree_id', '!=', False)])

        for employee in employees:
            employee_degree_code = employee.degree_id.code

            if employee_degree_code and self._check_identication_id(employee.identification_id) == 0:

                cargo_code = employee.occupational_category_id.code

                employee_age_range_code = employee.age_range_id.code

                employee_contract_type_code = employee.contract_hr_type_id.code

                if employee_contract_type_code == 'I':
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                            [('name', '=', 'Indeterminado')], limit=1).code
                else:
                    employee_contract_type_code = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                            [('name', '=', 'Determinado')], limit=1).code

                if cargo_code == 'TEC':
                    cargo_code = '2000'
                elif cargo_code == 'ADM':
                    cargo_code = '5000'
                elif cargo_code == 'OBR':
                    cargo_code = '1000'
                elif cargo_code == 'SER':
                    cargo_code = '3000'
                elif cargo_code == 'DIR':
                    cargo_code = '4000'
                else:
                    cargo_code = '1000'

                persona_ocupado_code = ministry_code + entity_code + employee_degree_code + str(
                        municipality_code) + str(
                        state_code) + employee_age_range_code + employee_contract_type_code + str(
                        actual_year) + employee.identification_id + ministry_code + entity_code + employee_degree_code + str(
                        municipality_code) + str(
                        state_code) + employee_age_range_code + employee_contract_type_code + str(
                        actual_year)

                node_datos = ET.SubElement(node_person_ocupada, "datos")

                item_id_persona_ocupado = ET.SubElement(node_datos, "id_persona_ocupado")
                item_id_persona_ocupado.text = persona_ocupado_code

                item_id_persona = ET.SubElement(node_datos, "id_persona")
                item_id_persona.text = ministry_code + entity_code + employee_degree_code + str(
                        municipality_code) + str(
                        state_code) + employee_age_range_code + employee_contract_type_code + str(
                        actual_year) + employee.identification_id

                item_id_ocupado = ET.SubElement(node_datos, "id_ocupado")
                item_id_ocupado.text = ministry_code + entity_code + employee_degree_code + str(
                        municipality_code) + str(
                        state_code) + employee_age_range_code + employee_contract_type_code + str(
                        actual_year)

                item_id_cargo = ET.SubElement(node_datos, "id_cargo")
                item_id_cargo.text = cargo_code

                item_fecha_alta = ET.SubElement(node_datos, "fecha_alta")
                fecha_alta = employee.admission_date
                fecha_alta = fecha_alta.split("-")
                fecha_alta = fecha_alta[2] + "-" + fecha_alta[1] + "-" + fecha_alta[0]
                item_fecha_alta.text = ustr(fecha_alta)

        node_fluctuacion = ET.SubElement(xmldoc, "tb_sm_fluctuacion")

        fluctuacion_sql_query = """select count(hr_employee.degree_id), l10n_cu_hlg_uforce_degree.code, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_hire_drop_record.record_date from hr_employee, l10n_cu_hlg_uforce_hire_drop_record, l10n_cu_hlg_uforce_degree,
                                                hr_contract_supplement_motive  where hr_employee.id = l10n_cu_hlg_uforce_hire_drop_record.employee_id and
                                                l10n_cu_hlg_uforce_hire_drop_record.record_type = 'drop' and hr_contract_supplement_motive.id = l10n_cu_hlg_uforce_hire_drop_record.motive_id and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id
                                                and hr_employee.degree_id is not null and l10n_cu_hlg_uforce_hire_drop_record.record_date >= %s group by degree_id, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_hire_drop_record.record_date
                                                """
        year_query = datetime.today().year
        date_query = str(year_query) + '-01-01'

        self.env.cr.execute(fluctuacion_sql_query, (date_query,))
        fluctuates = self.env.cr.fetchall()

        for fluctuate in fluctuates:
            code_motive = ''
            if str(fluctuate[2]) == '1':
                code_motive = '1010'
            elif str(fluctuate[2]) == '2':
                code_motive = '1011'
            elif str(fluctuate[2]) == '3':
                code_motive = '1026'
            elif str(fluctuate[2]) == '4':
                code_motive = '1027'
            elif str(fluctuate[2]) == '5':
                code_motive = '1010'
            elif str(fluctuate[2]) == '6':
                code_motive = '1010'
            elif str(fluctuate[2]) == '7':
                code_motive = '1010'
            else:
                code_motive = '1010'

            fluctuacion_code = entity_code + str(municipality_code) + code_motive + str(fluctuate[1]) + str(
                actual_year)
            node_datos = ET.SubElement(node_fluctuacion, "datos")

            item_id_fluctuacion = ET.SubElement(node_datos, "id_fluctuacion")
            item_id_fluctuacion.text = fluctuacion_code

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            item_id_causal = ET.SubElement(node_datos, "id_causal")
            item_id_causal.text = code_motive

            item_id_carrera = ET.SubElement(node_datos, "id_carrera")
            item_id_carrera.text = fluctuate[1]

            item_cantidad = ET.SubElement(node_datos, "cantidad")
            item_cantidad.text = str(fluctuate[0])

            item_year = ET.SubElement(node_datos, "anno_realizacion")
            item_year.text = str(actual_year)

            item_otra = ET.SubElement(node_datos, "otra")

        node_persona_fluctuacion = ET.SubElement(xmldoc, "tb_sm_persona_fluctuacion")

        fluctuacion_persona_sql_query = """select hr_employee.identification_id, hr_employee.degree_id, l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_age_range.code, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_hire_drop_record.record_date, l10n_cu_hlg_uforce_contract_hr_type.code, hr_employee.occupational_category_id from hr_employee, l10n_cu_hlg_uforce_hire_drop_record, l10n_cu_hlg_uforce_degree,
                                                hr_contract_supplement_motive, l10n_cu_hlg_uforce_age_range, l10n_cu_hlg_uforce_contract_hr_type   where hr_employee.id = l10n_cu_hlg_uforce_hire_drop_record.employee_id and l10n_cu_hlg_uforce_age_range.id = hr_employee.age_range_id and
                                                l10n_cu_hlg_uforce_hire_drop_record.record_type = 'drop' and hr_contract_supplement_motive.id = l10n_cu_hlg_uforce_hire_drop_record.motive_id and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id and hr_employee.contract_hr_type_id = l10n_cu_hlg_uforce_contract_hr_type.id
                                                and hr_employee.degree_id is not null and l10n_cu_hlg_uforce_hire_drop_record.record_date >= %s """

        self.env.cr.execute(fluctuacion_persona_sql_query, (date_query,))
        fluctuates_person = self.env.cr.fetchall()

        for fluctuate_person in fluctuates_person:
            node_datos = ET.SubElement(node_persona_fluctuacion, "datos")

            code_motive = ''
            if fluctuate_person[4] == '1':
                code_motive = '1010'
            elif fluctuate_person[4] == '2':
                code_motive = '1011'
            elif fluctuate_person[4] == '3':
                code_motive = '1026'
            elif fluctuate_person[4] == '4':
                code_motive = '1027'
            elif fluctuate_person[4] == '5':
                code_motive = '1010'
            elif fluctuate_person[4] == '6':
                code_motive = '1010'
            elif fluctuate_person[4] == '7':
                code_motive = '1010'
            else:
                code_motive = '1010'

            cargo_code = self.env['l10n_cu_hlg_hr.occupational_category'].search([('id', '=', fluctuate_person[7])],
                                                                                 limit=1).code

            if cargo_code == 'TEC':
                cargo_code = '2000'
            elif cargo_code == 'ADM':
                cargo_code = '5000'
            elif cargo_code == 'OBR':
                cargo_code = '1000'
            elif cargo_code == 'SER':
                cargo_code = '3000'
            elif cargo_code == 'DIR':
                cargo_code = '4000'
            else:
                cargo_code = '1000'

            contract_type = '3401'

            if fluctuate_person[6] == 'I':
                contract_type = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Indeterminado')], limit=1).code
            else:
                contract_type = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Determinado')], limit=1).code

            persona_fluctuacion_code = ministry_code + entity_code + fluctuate_person[2] + str(municipality_code) + str(state_code) + \
                                       fluctuate_person[3] + contract_type + str(actual_year) + fluctuate_person[
                                           0] + entity_code + str(municipality_code) + code_motive + fluctuate_person[
                                           2] + str(actual_year)

            item_id_persona_fluctuacion = ET.SubElement(node_datos, "id_persona_fluctuacion")
            item_id_persona_fluctuacion.text = persona_fluctuacion_code

            item_id_persona = ET.SubElement(node_datos, "id_persona")
            item_id_persona.text = ministry_code + entity_code + fluctuate_person[2] + str(municipality_code) + str(state_code) + \
                                   fluctuate_person[3] + contract_type + str(actual_year) + fluctuate_person[0]

            item_id_fluctuacion = ET.SubElement(node_datos, "id_fluctuacion")
            item_id_fluctuacion.text = entity_code + str(municipality_code) + code_motive + fluctuate_person[2] + str(
                actual_year)

            item_id_cargo = ET.SubElement(node_datos, "id_cargo")
            item_id_cargo.text = cargo_code

            item_fecha_baja = ET.SubElement(node_datos, "fecha_baja")
            item_fecha_baja.text = fluctuate_person[5]

        return xmldoc

    @api.multi
    def export_demands_hire_drops(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        xmldoc = ET.Element("ModMatriz")
        xmldoc.set('Fecha', str(datetime.today().date()))
        xmldoc.set('Hora', str(datetime.today().hour) + ":" + str(datetime.today().minute))
        actual_year = datetime.today().year

        node_demanda_graduados = ET.SubElement(xmldoc, "tb_sm_demanda_graduados")

        demand_graduates = self.env['l10n_cu_hlg_uforce.graduates_demand'].search([])
        entity_code = self.env.user.company_id.gforza_code
        municipality_code = self.env.user.company_id.partner_id.municipality_id.external_id
        ministry_code = self.env.user.company_id.partner_id.ministry_id.code
        state_code = self.env.user.company_id.partner_id.state_id.external_id

        if not ministry_code or not entity_code or not municipality_code or not state_code:
            raise ValidationError(_('Please, check the entity settings!'))

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_demanda_graduados, "datos")
            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = demand_graduate.code_ftc3

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            codeDegree = self.env['l10n_cu_hlg_uforce.degree'].search(
                [('id', '=', demand_graduate.degree_id.id)], limit=1).code

            item_id_carrera_demandada = ET.SubElement(node_datos, "id_carrera_demandada")
            item_id_carrera_demandada.text = codeDegree

            item_ano_realizacion = ET.SubElement(node_datos, "ano_realizacion")
            item_ano_realizacion.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

            node_datos = ET.SubElement(node_demanda_graduados, "datos")

            # FOR FTC4
            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = demand_graduate.code_ftc4

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            codeDegree = self.env['l10n_cu_hlg_uforce.degree'].search(
                [('id', '=', demand_graduate.degree_id.id)], limit=1).code

            item_id_carrera_demandada = ET.SubElement(node_datos, "id_carrera_demandada")
            item_id_carrera_demandada.text = codeDegree

            item_ano_realizacion = ET.SubElement(node_datos, "ano_realizacion")
            item_ano_realizacion.text = str(actual_year)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the demands line ftc3
        node_ftc3 = ET.SubElement(xmldoc, "tb_sm_modelo_ftc3")

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_ftc3, "datos")
            code_demanda_carrera = demand_graduate.code_ftc3

            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = code_demanda_carrera
            # search the period
            period_one_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 1))], limit=1).id
            demand_ftc3_one_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_one_id)], limit=1).quantity
            item_ano_mas_uno = ET.SubElement(node_datos, "ano_mas_uno")
            item_ano_mas_uno.text = str(demand_ftc3_one_quantity)

            period_two_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 2))], limit=1).id
            demand_ftc3_two_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_two_id)], limit=1).quantity
            item_ano_mas_dos = ET.SubElement(node_datos, "ano_mas_dos")
            item_ano_mas_dos.text = str(demand_ftc3_two_quantity)

            period_three_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 3))],
                                                                       limit=1).id
            demand_ftc3_three_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_three_id)], limit=1).quantity
            item_ano_mas_tres = ET.SubElement(node_datos, "ano_mas_tres")
            item_ano_mas_tres.text = str(demand_ftc3_three_quantity)

            period_four_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 4))], limit=1).id
            demand_ftc3_four_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_four_id)], limit=1).quantity
            item_ano_mas_cuatro = ET.SubElement(node_datos, "ano_mas_cuatro")
            item_ano_mas_cuatro.text = str(demand_ftc3_four_quantity)

            period_five_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 5))], limit=1).id
            demand_ftc3_five_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_five_id)], limit=1).quantity
            item_ano_mas_cinco = ET.SubElement(node_datos, "ano_mas_cinco")
            item_ano_mas_cinco.text = str(demand_ftc3_four_quantity)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        # the demands line ftc4
        node_ftc4 = ET.SubElement(xmldoc, "tb_sm_modelo_ftc4")

        for demand_graduate in demand_graduates:
            node_datos = ET.SubElement(node_ftc4, "datos")
            code_demanda_carrera = demand_graduate.code_ftc4

            item_id_demanda_carrera = ET.SubElement(node_datos, "id_demanda_carrera")
            item_id_demanda_carrera.text = code_demanda_carrera
            # search the period
            period_six_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 1))], limit=1).id
            demand_ftc3_six_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_six_id)], limit=1).quantity
            item_ano_mas_seis = ET.SubElement(node_datos, "ano_mas_seis")
            item_ano_mas_seis.text = str(demand_ftc3_six_quantity)

            period_seven_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 2))],
                                                                       limit=1).id
            demand_ftc3_seven_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_seven_id)], limit=1).quantity
            item_ano_mas_siete = ET.SubElement(node_datos, "ano_mas_siete")
            item_ano_mas_siete.text = str(demand_ftc3_seven_quantity)

            period_eigth_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 3))],
                                                                       limit=1).id
            demand_ftc3_eigth_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_eigth_id)], limit=1).quantity
            item_ano_mas_ocho = ET.SubElement(node_datos, "ano_mas_ocho")
            item_ano_mas_ocho.text = str(demand_ftc3_eigth_quantity)

            period_nine_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 4))], limit=1).id
            demand_ftc3_nine_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_nine_id)], limit=1).quantity
            item_ano_mas_nueve = ET.SubElement(node_datos, "ano_mas_nueve")
            item_ano_mas_nueve.text = str(demand_ftc3_nine_quantity)

            period_ten_id = self.env['l10n_cu_period.period'].search([('name', '=', str(actual_year + 5))], limit=1).id
            demand_ftc3_ten_quantity = self.env['l10n_cu_hlg_uforce.graduates_demand_line'].search(
                ['&', ('demand_id', '=', demand_graduate.id), ('period_id', '=', period_ten_id)], limit=1).quantity
            item_ano_mas_diez = ET.SubElement(node_datos, "ano_mas_diez")
            item_ano_mas_diez.text = str(demand_ftc3_ten_quantity)

            item_estado = ET.SubElement(node_datos, "estado")
            item_estado.text = str(2)

            item_est_replica = ET.SubElement(node_datos, "est_replica")
            item_est_replica.text = str(1)

        node_fluctuacion = ET.SubElement(xmldoc, "tb_sm_fluctuacion")

        fluctuacion_sql_query = """select count(hr_employee.degree_id), l10n_cu_hlg_uforce_degree.code, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_hire_drop_record.record_date from hr_employee, l10n_cu_hlg_uforce_hire_drop_record, l10n_cu_hlg_uforce_degree,
                                                hr_contract_supplement_motive  where hr_employee.id = l10n_cu_hlg_uforce_hire_drop_record.employee_id and
                                                l10n_cu_hlg_uforce_hire_drop_record.record_type = 'drop' and hr_contract_supplement_motive.id = l10n_cu_hlg_uforce_hire_drop_record.motive_id and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id
                                                and hr_employee.degree_id is not null and l10n_cu_hlg_uforce_hire_drop_record.record_date >= %s group by degree_id, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_hire_drop_record.record_date
                                                """
        year_query = datetime.today().year
        date_query = str(year_query) + '-01-01'

        self.env.cr.execute(fluctuacion_sql_query, (date_query,))
        fluctuates = self.env.cr.fetchall()

        for fluctuate in fluctuates:
            code_motive = ''
            if str(fluctuate[2]) == '1':
                code_motive = '1010'
            elif str(fluctuate[2]) == '2':
                code_motive = '1011'
            elif str(fluctuate[2]) == '3':
                code_motive = '1026'
            elif str(fluctuate[2]) == '4':
                code_motive = '1027'
            elif str(fluctuate[2]) == '5':
                code_motive = '1010'
            elif str(fluctuate[2]) == '6':
                code_motive = '1010'
            elif str(fluctuate[2]) == '7':
                code_motive = '1010'
            else:
                code_motive = '1010'

            fluctuacion_code = entity_code + str(municipality_code) + code_motive + str(fluctuate[1]) + str(
                actual_year)
            node_datos = ET.SubElement(node_fluctuacion, "datos")

            item_id_fluctuacion = ET.SubElement(node_datos, "id_fluctuacion")
            item_id_fluctuacion.text = fluctuacion_code

            item_id_entidad = ET.SubElement(node_datos, "id_entidad")
            item_id_entidad.text = entity_code

            item_id_munic_entidad = ET.SubElement(node_datos, "id_munic_entidad")
            item_id_munic_entidad.text = str(municipality_code)

            item_id_causal = ET.SubElement(node_datos, "id_causal")
            item_id_causal.text = code_motive

            item_id_carrera = ET.SubElement(node_datos, "id_carrera")
            item_id_carrera.text = fluctuate[1]

            item_cantidad = ET.SubElement(node_datos, "cantidad")
            item_cantidad.text = str(fluctuate[0])

            item_year = ET.SubElement(node_datos, "anno_realizacion")
            item_year.text = str(actual_year)

            item_otra = ET.SubElement(node_datos, "otra")

        node_persona_fluctuacion = ET.SubElement(xmldoc, "tb_sm_persona_fluctuacion")

        fluctuacion_persona_sql_query = """select hr_employee.identification_id, hr_employee.degree_id, l10n_cu_hlg_uforce_degree.code, l10n_cu_hlg_uforce_age_range.code, hr_contract_supplement_motive.code, l10n_cu_hlg_uforce_hire_drop_record.record_date, l10n_cu_hlg_uforce_contract_hr_type.code, hr_employee.occupational_category_id from hr_employee, l10n_cu_hlg_uforce_hire_drop_record, l10n_cu_hlg_uforce_degree,
                                                hr_contract_supplement_motive, l10n_cu_hlg_uforce_age_range, l10n_cu_hlg_uforce_contract_hr_type   where hr_employee.id = l10n_cu_hlg_uforce_hire_drop_record.employee_id and l10n_cu_hlg_uforce_age_range.id = hr_employee.age_range_id and
                                                l10n_cu_hlg_uforce_hire_drop_record.record_type = 'drop' and hr_contract_supplement_motive.id = l10n_cu_hlg_uforce_hire_drop_record.motive_id and l10n_cu_hlg_uforce_degree.id = hr_employee.degree_id and hr_employee.contract_hr_type_id = l10n_cu_hlg_uforce_contract_hr_type.id
                                                and hr_employee.degree_id is not null and l10n_cu_hlg_uforce_hire_drop_record.record_date >= %s """

        self.env.cr.execute(fluctuacion_persona_sql_query, (date_query,))
        fluctuates_person = self.env.cr.fetchall()

        for fluctuate_person in fluctuates_person:
            node_datos = ET.SubElement(node_persona_fluctuacion, "datos")

            code_motive = ''
            if fluctuate_person[4] == '1':
                code_motive = '1010'
            elif fluctuate_person[4] == '2':
                code_motive = '1011'
            elif fluctuate_person[4] == '3':
                code_motive = '1026'
            elif fluctuate_person[4] == '4':
                code_motive = '1027'
            elif fluctuate_person[4] == '5':
                code_motive = '1010'
            elif fluctuate_person[4] == '6':
                code_motive = '1010'
            elif fluctuate_person[4] == '7':
                code_motive = '1010'
            else:
                code_motive = '1010'

            cargo_code = self.env['l10n_cu_hlg_hr.occupational_category'].search([('id', '=', fluctuate_person[7])],
                                                                                 limit=1).code

            if cargo_code == 'TEC':
                cargo_code = '2000'
            elif cargo_code == 'ADM':
                cargo_code = '5000'
            elif cargo_code == 'OBR':
                cargo_code = '1000'
            elif cargo_code == 'SER':
                cargo_code = '3000'
            elif cargo_code == 'DIR':
                cargo_code = '4000'
            else:
                cargo_code = '1000'

            contract_type = '3401'

            if fluctuate_person[6] == 'I':
                contract_type = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Indeterminado')], limit=1).code
            else:
                contract_type = self.env['l10n_cu_hlg_uforce.contract_type'].search(
                    [('name', '=', 'Determinado')], limit=1).code

            persona_fluctuacion_code = ministry_code + entity_code + fluctuate_person[2] + str(municipality_code) + str(state_code) + \
                                       fluctuate_person[3] + contract_type + str(actual_year) + fluctuate_person[
                                           0] + entity_code + str(municipality_code) + code_motive + fluctuate_person[
                                           2] + str(actual_year)

            item_id_persona_fluctuacion = ET.SubElement(node_datos, "id_persona_fluctuacion")
            item_id_persona_fluctuacion.text = persona_fluctuacion_code

            item_id_persona = ET.SubElement(node_datos, "id_persona")
            item_id_persona.text = ministry_code + entity_code + fluctuate_person[2] + str(municipality_code) + str(state_code) + \
                                   fluctuate_person[3] + contract_type + str(actual_year) + fluctuate_person[0]

            item_id_fluctuacion = ET.SubElement(node_datos, "id_fluctuacion")
            item_id_fluctuacion.text = entity_code + str(municipality_code) + code_motive + fluctuate_person[2] + str(
                actual_year)

            item_id_cargo = ET.SubElement(node_datos, "id_cargo")
            item_id_cargo.text = cargo_code

            item_fecha_baja = ET.SubElement(node_datos, "fecha_baja")
            item_fecha_baja.text = fluctuate_person[5]

        return xmldoc

    @api.multi
    def action_export_to_gforza(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        company_name = self.env.user.company_id.name
        company_name = company_name.replace(' ', '_')
        year_actual = str(datetime.today().year)
        self.filename_export = ustr(company_name + "_" + year_actual + ".xml")
        xdec = """<?xml version="1.0" standalone="no"?>"""

        if self.demands == True and self.employees == True and self.hire_drop == True:
            self.file_export = base64.encodestring(
                self.tostring(self.export_all(), encoding='utf-8', declaration=xdec))

            if self.existBadCi():
                xls_io = l10n_cu_hlg_uforce_report_employee_xls.ReportEmployeeExcel(self, self._cr, self._uid,
                                                                                    self._context).get_data()
                self.filename_xls_export = ustr(company_name + "_" + year_actual + "_"+"Problemas_CI"+ ".xls")
                self.file_xls_export = base64.encodestring(xls_io.getvalue())

            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'l10n_cu_hlg_uforce.update_from_gforza_wizard',
                'type': 'ir.actions.do_nothing',
                'target': 'new'
            }

        #get employees
        if self.employees and not self.demands and not self.hire_drop:
            self.file_export = base64.encodestring(
                 self.tostring(self.export_employees(), encoding='utf-8', declaration=xdec))

            if self.existBadCi():
                xls_io = l10n_cu_hlg_uforce_report_employee_xls.ReportEmployeeExcel(self, self._cr, self._uid,
                                                                                    self._context).get_data()
                self.filename_xls_export = ustr(company_name + "_" + year_actual + "_"+"Problemas_CI"+ ".xls")
                self.file_xls_export = base64.encodestring(xls_io.getvalue())

            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'l10n_cu_hlg_uforce.update_from_gforza_wizard',
                'type': 'ir.actions.do_nothing',
                'target': 'new'
            }

        if self.employees == False and self.demands == True and self.hire_drop == False:
            self.file_export = base64.encodestring(
                self.tostring(self.export_demands(), encoding='utf-8', declaration=xdec))
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'l10n_cu_hlg_uforce.update_from_gforza_wizard',
                'type': 'ir.actions.do_nothing',
                'target': 'new'
            }

        if self.employees == False and self.demands == False and self.hire_drop == True:
            self.file_export = base64.encodestring(
                self.tostring(self.export_hire_drop(), encoding='utf-8', declaration=xdec))
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'l10n_cu_hlg_uforce.update_from_gforza_wizard',
                'type': 'ir.actions.do_nothing',
                'target': 'new'
            }

        if self.employees == True and self.demands == True and self.hire_drop == False:
            self.file_export = base64.encodestring(
                self.tostring(self.export_employees_demands(), encoding='utf-8', declaration=xdec))

            if self.existBadCi():
                xls_io = l10n_cu_hlg_uforce_report_employee_xls.ReportEmployeeExcel(self, self._cr, self._uid,
                                                                                    self._context).get_data()
                self.filename_xls_export = ustr(company_name + "_" + year_actual + "_"+"Problemas_CI"+ ".xls")
                self.file_xls_export = base64.encodestring(xls_io.getvalue())
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'l10n_cu_hlg_uforce.update_from_gforza_wizard',
                'type': 'ir.actions.do_nothing',
                'target': 'new'
            }

        if self.employees == True and self.demands == False and self.hire_drop == True:
            self.file_export = base64.encodestring(
                self.tostring(self.export_employees_hire_drops(), encoding='utf-8', declaration=xdec))

            if self.existBadCi():
                xls_io = l10n_cu_hlg_uforce_report_employee_xls.ReportEmployeeExcel(self, self._cr, self._uid, self._context).get_data()
                self.filename_xls_export = ustr(company_name + "_" + year_actual + "_"+"Problemas_CI"+ ".xls")
                self.file_xls_export = base64.encodestring(xls_io.getvalue())
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'l10n_cu_hlg_uforce.update_from_gforza_wizard',
                'type': 'ir.actions.do_nothing',
                'target': 'new'
            }

        if self.employees == False and self.demands == True and self.hire_drop == True:
            self.file_export = base64.encodestring(
                self.tostring(self.export_demands_hire_drops(), encoding='utf-8', declaration=xdec))
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'l10n_cu_hlg_uforce.update_from_gforza_wizard',
                'type': 'ir.actions.do_nothing',
                'target': 'new'
            }


        if self.employees == False and self.demands == False and self.hire_drop == False:
            raise ValidationError(_("Error: you must select options to export !!"))

    ################################# UPDATE FROM GFORZA ###################################################################

    @api.multi
    def action_update_from_gforza(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        path = self._save_file()

        doc = xml.dom.minidom.parse(path)

        if doc.getElementsByTagName("id_ocupados"):
            listEmployed = doc.getElementsByTagName("id_ocupados")
            listDictEmployedDegre = []
            data = {}

            i = 0
            for item in listEmployed:
                codEmployed = self.getNodeText(doc.getElementsByTagName("id_ocupados")[i])
                codEmployed = codEmployed[0:len(codEmployed) - 4]
                codDegree = self.getNodeText(doc.getElementsByTagName("id_cod_carrera")[i])
                codMunicipality = self.getNodeText(doc.getElementsByTagName("id_municipio_ocupado")[i])
                codContractType = self.getNodeText(doc.getElementsByTagName("id_tipo_plaza")[i])
                codAgeRange = self.getNodeText(doc.getElementsByTagName("id_rango_edad")[i])
                countGraduates = self.getNodeText(doc.getElementsByTagName("cant_graduados")[i])
                codeEntity = self.getNodeText(doc.getElementsByTagName("id_codigo_entidad")[i])
                yearDo = datetime.today().year
                i += 1
                data = {'codEmployed': codEmployed,
                        'codDegree': codDegree
                        }
                listDictEmployedDegre.append(data)

            listPerson = doc.getElementsByTagName("id_persona")
            i = 0
            for item in listPerson:
                codPDegree = ''
                codPersonEmployed = self.getNodeText(doc.getElementsByTagName("id_persona")[i])

                codPerson = codPersonEmployed[0:(len(codPersonEmployed) - 11)]
                ci = codPersonEmployed[- 11:]
                codPerson = codPersonEmployed[0:len(codPersonEmployed) - 15]
                i += 1
                employee = self.env['hr.employee'].search(
                    [('identification_id', '=', ci)])

                if employee:
                    # search codDegree for this person
                    for item in listDictEmployedDegre:
                        if item.get('codEmployed') == codPerson:
                            codPDegree = item.get('codDegree')
                            break
                    degree_id = self.env['l10n_cu_hlg_uforce.degree'].search([('code', '=', codPDegree)], limit=1).id
                    employee.write({'degree_id': degree_id})
        else:
            raise ValidationError(_("Error: the XML file not have employees !!"))
        # create or update graduate demands
        # IMPORTANT THE TAG <id_demanda_carrera> repeat in others NODE, corresponding with the demands line here

        if doc.getElementsByTagName("tb_sm_demanda_graduados"):
            demandGraduatesObject = self.env['l10n_cu_hlg_uforce.graduates_demand']
            demandGraduatesLineObject = self.env['l10n_cu_hlg_uforce.graduates_demand_line']

            demand = doc.getElementsByTagName("tb_sm_demanda_graduados")[0]
            listDemandGraduates = demand.getElementsByTagName("datos")

            for item in listDemandGraduates:
                codDemanDegree = self.getNodeText(item.getElementsByTagName("id_carrera_demandada")[0])
                yearMake = self.getNodeText(item.getElementsByTagName("ano_realizacion")[0])
                codeDemand = self.getNodeText(item.getElementsByTagName("id_demanda_carrera")[0])
                entity_code = self.env.user.company_id.gforza_code
                municipality_code = self.getNodeText(item.getElementsByTagName("id_munic_entidad")[0])

                degree_id = self.env['l10n_cu_hlg_uforce.degree'].search([('code', '=', codDemanDegree)],
                                                                                limit=1).id
                period_id = self.env['l10n_cu_period.period'].search([('name', '=', yearMake)], limit=1).id

                municipality_id = self.env['l10n_cu_base.municipality'].search(
                    [('external_id', '=', municipality_code)], limit=1)
                state_id = self.env['res.country.state'].search([('id', '=', municipality_id.state_id.id)], limit=1).id
                entity_id = self.env['res.partner'].search([('gforza_code', '=', entity_code)], limit=1)
                organism_id = self.env.user.company_id.organism_id
                ministry_id = self.env['l10n_cu.ministry'].search([('id', '=', organism_id.ministry_id.id)], limit=1).id

                demandGraduates = demandGraduatesObject.search(
                    ['|', ('code_ftc3', '=', codeDemand), ('code_ftc4', '=', codeDemand)])

                if demandGraduates:
                    # First update DemandGraduates
                    # see if code is for ftc3 or ftc4
                    code_ftc3 = ''
                    code_ftc4 = ''
                    if codeDemand[-1:] == '3':
                        code_ftc3 = codeDemand
                        code_ftc4 = codeDemand[0:len(codeDemand) - 1] + '4'
                    else:
                        code_ftc4 = codeDemand
                        code_ftc3 = codeDemand[0:len(codeDemand) - 1] + '3'

                    demandGraduates.write({
                        'code_ftc3': code_ftc3,
                        'code_ftc4': code_ftc4,
                        'ministry_id': ministry_id,
                        'organism_id': organism_id.id,
                        'state_id': state_id,
                        'municipality_id': municipality_id.id,
                        'degree_id': degree_id,
                        'period_id': period_id

                    })
                    # second update demandsLine

                    # for each demand search in ftc3 and ftc4 to obtains the demands line data

                    ftc3 = doc.getElementsByTagName("tb_sm_modelo_ftc3")[0]
                    listDemandLines = ftc3.getElementsByTagName("datos")

                    for ftc in listDemandLines:
                        if self.getNodeText(ftc.getElementsByTagName("id_demanda_carrera")[0]) == codeDemand:
                            period_id1 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 1))]).id
                            quantity1 = self.getNodeText(ftc.getElementsByTagName("ano_mas_uno")[0])
                            period_id2 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 2))]).id
                            quantity2 = self.getNodeText(ftc.getElementsByTagName("ano_mas_dos")[0])
                            period_id3 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 3))]).id
                            quantity3 = self.getNodeText(ftc.getElementsByTagName("ano_mas_tres")[0])
                            period_id4 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 4))]).id
                            quantity4 = self.getNodeText(ftc.getElementsByTagName("ano_mas_cuatro")[0])
                            period_id5 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 5))]).id
                            quantity5 = self.getNodeText(ftc.getElementsByTagName("ano_mas_cinco")[0])
                            demand_id = demandGraduatesObject.search(
                                ['|', ('code_ftc3', '=', codeDemand), ('code_ftc4', '=', codeDemand)]).id

                            demandLine1 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id1)])
                            demandLine1.write({
                                'demand_id': demand_id,
                                'period_id': period_id1,
                                'quantity': quantity1
                            })

                            demandLine2 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id2)])
                            demandLine2.write({
                                'demand_id': demand_id,
                                'period_id': period_id2,
                                'quantity': quantity2
                            })

                            demandLine3 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id3)])
                            demandLine3.write({
                                'demand_id': demand_id,
                                'period_id': period_id3,
                                'quantity': quantity3
                            })

                            demandLine4 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id4)])
                            demandLine4.write({
                                'demand_id': demand_id,
                                'period_id': period_id4,
                                'quantity': quantity4
                            })

                            demandLine5 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id5)])
                            demandLine5.write({
                                'demand_id': demand_id,
                                'period_id': period_id5,
                                'quantity': quantity5
                            })

                    ftc4 = doc.getElementsByTagName("tb_sm_modelo_ftc4")[0]
                    listDemandLines = ftc4.getElementsByTagName("datos")
                    for ftc in listDemandLines:
                        if self.getNodeText(ftc.getElementsByTagName("id_demanda_carrera")[0]) == codeDemand:
                            period_id6 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 6))]).id
                            quantity6 = self.getNodeText(ftc.getElementsByTagName("ano_mas_seis")[0])
                            period_id7 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 7))]).id
                            quantity7 = self.getNodeText(ftc.getElementsByTagName("ano_mas_siete")[0])
                            period_id8 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 8))]).id
                            quantity8 = self.getNodeText(ftc.getElementsByTagName("ano_mas_ocho")[0])
                            period_id9 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 9))]).id
                            quantity9 = self.getNodeText(ftc.getElementsByTagName("ano_mas_nueve")[0])
                            period_id10 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 10))]).id
                            quantity10 = self.getNodeText(ftc.getElementsByTagName("ano_mas_diez")[0])
                            demand_id = demandGraduatesObject.search(
                                ['|', ('code_ftc3', '=', codeDemand), ('code_ftc4', '=', codeDemand)]).id

                            demandLine6 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id6)])
                            demandLine6.write({
                                'demand_id': demand_id,
                                'period_id': period_id6,
                                'quantity': quantity6
                            })

                            demandLine7 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id7)])
                            demandLine7.write({
                                'demand_id': demand_id,
                                'period_id': period_id7,
                                'quantity': quantity7
                            })
                            demandLine8 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id8)])
                            demandLine8.write({
                                'demand_id': demand_id,
                                'period_id': period_id8,
                                'quantity': quantity8
                            })
                            demandLine9 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id9)])
                            demandLine9.write({
                                'demand_id': demand_id,
                                'period_id': period_id9,
                                'quantity': quantity9
                            })
                            demandLine10 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demandGraduates.id), ('period_id', '=', period_id10)])
                            demandLine10.write({
                                'demand_id': demand_id,
                                'period_id': period_id10,
                                'quantity': quantity10
                            })
                else:
                    # first create demandGraduates
                    # see if code is for ftc3 or ftc4
                    code_ftc3 = ''
                    code_ftc4 = ''
                    is_ftc3 = False

                    if codeDemand[-1:] == '3':
                        code_ftc3 = codeDemand
                        code_ftc4 = codeDemand[0:len(codeDemand) - 1] + '4'
                        is_ftc3 = True
                    else:
                        code_ftc4 = codeDemand
                        code_ftc3 = codeDemand[0:len(codeDemand) - 1] + '3'

                    demandGraduates.create({
                        'code_ftc3': code_ftc3,
                        'code_ftc4': code_ftc4,
                        'ministry_id': ministry_id,
                        'organism_id': organism_id.id,
                        'state_id': state_id,
                        'municipality_id': municipality_id.id,
                        'entity_id': self.env.user.company_id.id,
                        'degree_id': degree_id,
                        'period_id': period_id

                    })
                    demand_id = demandGraduatesObject.search(
                        ['|', ('code_ftc3', '=', codeDemand), ('code_ftc4', '=', codeDemand)]).id
                    # second create de DemandLines
                    # first i create in cero quantity
                    for i in range(1, 11):
                        period_id = self.env['l10n_cu_period.period'].search(
                            [('name', '=', str(datetime.today().year + i))]).id
                        quantity = 0

                        demandGraduatesLineObject.create({
                            'demand_id': demand_id,
                            'period_id': period_id,
                            'quantity': quantity,
                            'company_id': self.env.user.company_id.id
                        })

                    # for each demand search in ftc3 and ftc4 to obtains the demands line data

                    ftc3 = doc.getElementsByTagName("tb_sm_modelo_ftc3")[0]
                    listDemandLines = ftc3.getElementsByTagName("datos")

                    for ftc in listDemandLines:
                        if self.getNodeText(ftc.getElementsByTagName("id_demanda_carrera")[0]) == codeDemand:
                            period_id1 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 1))]).id
                            quantity1 = self.getNodeText(ftc.getElementsByTagName("ano_mas_uno")[0])
                            period_id2 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 2))]).id
                            quantity2 = self.getNodeText(ftc.getElementsByTagName("ano_mas_dos")[0])
                            period_id3 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 3))]).id
                            quantity3 = self.getNodeText(ftc.getElementsByTagName("ano_mas_tres")[0])
                            period_id4 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 4))]).id
                            quantity4 = self.getNodeText(ftc.getElementsByTagName("ano_mas_cuatro")[0])
                            period_id5 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 5))]).id
                            quantity5 = self.getNodeText(ftc.getElementsByTagName("ano_mas_cinco")[0])

                            demandLine1 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id1)])
                            demandLine1.write({
                                'demand_id': demand_id,
                                'period_id': period_id1,
                                'quantity': quantity
                            })

                            demandLine2 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id2)])
                            demandLine2.write({
                                'demand_id': demand_id,
                                'period_id': period_id2,
                                'quantity': quantity2
                            })

                            demandLine3 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id3)])
                            demandLine3.write({
                                'demand_id': demand_id,
                                'period_id': period_id3,
                                'quantity': quantity3
                            })

                            demandLine4 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id4)])
                            demandLine4.write({
                                'demand_id': demand_id,
                                'period_id': period_id4,
                                'quantity': quantity4
                            })

                            demandLine5 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id5)])
                            demandLine5.write({
                                'demand_id': demand_id,
                                'period_id': period_id5,
                                'quantity': quantity5
                            })

                    ftc4 = doc.getElementsByTagName("tb_sm_modelo_ftc4")[0]
                    listDemandLines = ftc4.getElementsByTagName("datos")
                    for ftc in listDemandLines:
                        if self.getNodeText(ftc.getElementsByTagName("id_demanda_carrera")[0]) == codeDemand:
                            period_id6 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 6))]).id
                            quantity6 = self.getNodeText(ftc.getElementsByTagName("ano_mas_seis")[0])
                            period_id7 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 7))]).id
                            quantity7 = self.getNodeText(ftc.getElementsByTagName("ano_mas_siete")[0])
                            period_id8 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 8))]).id
                            quantity8 = self.getNodeText(ftc.getElementsByTagName("ano_mas_ocho")[0])
                            period_id9 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 9))]).id
                            quantity9 = self.getNodeText(ftc.getElementsByTagName("ano_mas_nueve")[0])
                            period_id10 = self.env['l10n_cu_period.period'].search(
                                [('name', '=', str(datetime.today().year + 10))]).id
                            quantity10 = self.getNodeText(ftc.getElementsByTagName("ano_mas_diez")[0])

                            demandLine6 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id6)])
                            demandLine6.write({
                                'demand_id': demand_id,
                                'period_id': period_id6,
                                'quantity': quantity6
                            })

                            demandLine7 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id7)])
                            demandLine7.write({
                                'demand_id': demand_id,
                                'period_id': period_id7,
                                'quantity': quantity7
                            })
                            demandLine8 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id8)])
                            demandLine8.write({
                                'demand_id': demand_id,
                                'period_id': period_id8,
                                'quantity': quantity8
                            })
                            demandLine9 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id9)])
                            demandLine9.write({
                                'demand_id': demand_id,
                                'period_id': period_id9,
                                'quantity': quantity9

                            })
                            demandLine10 = demandGraduatesLineObject.search(
                                [('demand_id', '=', demand_id), ('period_id', '=', period_id10)])
                            demandLine10.write({
                                'demand_id': demand_id,
                                'period_id': period_id10,
                                'quantity': quantity10
                            })

        # end create or update demand graduates
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('l10n_cu_hlg_uforce.uforce_employee_menu_item').id},
        }
