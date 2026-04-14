# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class RegistryR1Resume(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        area = ''
        if data['all_company']:
            area = self.env.user.company_id.name
        else:
            area = self.env['enterprise_mgm_sys.work_area'].search([('id', '=', data['area_id'])], limit=1).name

        worksheet = workbook.add_worksheet(tools.ustr('Registro R1'))
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11})
        merge_format.set_text_wrap()
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 11})
        normal_format.set_text_wrap()
        normal_format_no_border = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vcenter', 'font_size': 11})
        normal_format_no_border.set_text_wrap()
        normal_center_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        normal_center_format.set_text_wrap()
        sign_format = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vdistributed', 'font_size': 10})
        sign_format.set_text_wrap()
        sign_format.set_indent(4)
        identification_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        worksheet.insert_image('A1', addons_manifest['hr_turei'][
            'addons_path'] + '/hr_turei/static/src/img/logo-landscape.jpg',
                               {'x_offset': 15, 'y_offset': 2, 'x_scale': 1.2, 'y_scale': 1.5})
        worksheet.merge_range('D1:G3', tools.ustr('Modelo para la realización del diagnóstico a cada nivel (R-1)'), merge_format)
        worksheet.merge_range('A1:C3', tools.ustr(''), merge_format)
        worksheet.merge_range('H1:I1', tools.ustr('Versión: 00'), identification_format)
        worksheet.merge_range('H2:I2', tools.ustr('Fecha de aprobación: 21/6/2018'), identification_format)
        worksheet.merge_range('H3:I3', tools.ustr('Código: M-DTD-03-R15'), identification_format)
        date = datetime.strptime(data['realization_date'], DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
        worksheet.merge_range('G5:I5', tools.ustr('Fecha de realización: %s' % date), normal_format_no_border)
        worksheet.merge_range('A6:D6', tools.ustr('Segmento o Unidad: %s' % area), normal_format_no_border)
        worksheet.merge_range('E6:I6', tools.ustr('Área de Trabajo:'), normal_format_no_border)

        worksheet.write('B8', tools.ustr('No'), merge_format)
        worksheet.merge_range('C8:D8', tools.ustr('Riesgo'), merge_format)
        worksheet.write('E8', tools.ustr('Clasificación del Riesgo'), merge_format)
        worksheet.write('F8', tools.ustr('Probabilidad'), merge_format)
        worksheet.write('G8', tools.ustr('Consecuencia'), merge_format)
        worksheet.write('H8', tools.ustr('Nivel del riesgo'), merge_format)

        worksheet.set_column('A1:A1', 11)
        worksheet.set_column('B1:B1', 5)
        worksheet.set_column('C1:C1', 11)
        worksheet.set_column('D1:D1', 19)
        worksheet.set_column('E1:E1', 14)
        worksheet.set_column('F1:F1', 14)
        worksheet.set_column('G1:G1', 14)
        worksheet.set_column('H1:H1', 15)
        worksheet.set_column('I1:I1', 8)

        i = 8
        count = 1
        if data['all_company']:
            lines = self.env['enterprise_mgm_sys.registryr1_line'].search([('registry_id.date', '>=', data['start']), ('registry_id.date', '<=', data['end']), ('level', '!=', 'trivial')])
        else:
            lines = self.env['enterprise_mgm_sys.registryr1_line'].search([('registry_id.date', '>=', data['start']), ('registry_id.date', '<=', data['end']), ('registry_id.area_id', '=', data['area_id'])])
        risks = {}
        for record in lines:
            if record.risk_id.id in risks:
                continue
            else:
                risks[record.risk_id.id] = True
            worksheet.write(i, 1, tools.ustr(count), normal_format)
            worksheet.merge_range(i, 2, i, 3, tools.ustr(record.risk_id.name), normal_format)
            worksheet.write(i, 4, tools.ustr(dict(self.env['enterprise_mgm_sys.registryr1_line'].fields_get(allfields=['classification'])['classification']['selection'])[record.classification]), normal_format)
            worksheet.write(i, 5, tools.ustr(dict(self.env['enterprise_mgm_sys.registryr1_line'].fields_get(allfields=['probability'])['probability']['selection'])[record.probability]), normal_format)
            worksheet.write(i, 6, tools.ustr(dict(self.env['enterprise_mgm_sys.registryr1_line'].fields_get(allfields=['consequence'])['consequence']['selection'])[record.consequence]), normal_format)
            worksheet.write(i, 7, tools.ustr(dict(self.env['enterprise_mgm_sys.registryr1_line'].fields_get(allfields=['level'])['level']['selection'])[record.level]), normal_format)
            i += 1
            count += 1

RegistryR1Resume('report.enterprise_mgm_sys.registry_r1_resume_report', 'enterprise_mgm_sys.registryr1')
