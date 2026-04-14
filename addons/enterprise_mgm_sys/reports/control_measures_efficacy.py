# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ControlMeasuresEfficacy(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet(tools.ustr('R4'))
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
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11})
        normal_center_format.set_text_wrap()
        sign_format = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vdistributed', 'font_size': 10})
        sign_format.set_text_wrap()
        sign_format.set_indent(4)
        identification_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        worksheet.insert_image('A1', addons_manifest['hr_turei'][
            'addons_path'] + '/enterprise_mgm_sys/static/src/img/logo-landscape.jpg',
                               {'x_offset': 15, 'y_offset': 2, 'x_scale': 1.2, 'y_scale': 1.5})
        worksheet.merge_range('C1:I3', tools.ustr('Eficacia de las medidas de control (R-4)'), merge_format)
        worksheet.merge_range('A1:B3', tools.ustr(''), merge_format)
        worksheet.merge_range('J1:M1', tools.ustr('Versión: 00'), identification_format)
        worksheet.merge_range('J2:M2', tools.ustr('Fecha de aprobación: 24/7/2018'), identification_format)
        worksheet.merge_range('J3:M3', tools.ustr('Código: M-DTD-03-R-23'), identification_format)
        worksheet.merge_range('A6:M6', tools.ustr('Proceso: %s' % lines.process_id.name), normal_format_no_border)
        date = datetime.strptime(lines.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')

        worksheet.merge_range('D7:F7', tools.ustr('Evaluación INICIAL'), merge_format)
        worksheet.merge_range('J7:L7', tools.ustr('Evaluación ACTUAL'), merge_format)
        worksheet.write('A8', tools.ustr('Objetivo'), merge_format)
        worksheet.write('B8', tools.ustr('Cumplimiento SI (5) NO(2)'), merge_format)
        worksheet.write('C8', tools.ustr('Riesgo'), merge_format)
        worksheet.write('D8', tools.ustr('Probabi-lidad'), merge_format)
        worksheet.write('E8', tools.ustr('Conse-cuencia'), merge_format)
        worksheet.write('F8', tools.ustr('Eva-luación'), merge_format)
        worksheet.write('G8', tools.ustr('Medidas'), merge_format)
        worksheet.write('H8', tools.ustr('F/C'), merge_format)
        worksheet.write('I8', tools.ustr('Respon-sable'), merge_format)
        worksheet.write('J8', tools.ustr('Probabi-lidad'), merge_format)
        worksheet.write('K8', tools.ustr('Conse-cuencia'), merge_format)
        worksheet.write('L8', tools.ustr('Eva-luación'), merge_format)
        worksheet.write('M8', tools.ustr('Eficaz (5), No Eficaz (2)'), merge_format)

        worksheet.set_column('A1:A1', 30)
        worksheet.set_column('B1:B1', 14)
        worksheet.set_column('C1:C1', 18)
        worksheet.set_column('D1:D1', 8)
        worksheet.set_column('E1:E1', 8)
        worksheet.set_column('F1:F1', 8)
        worksheet.set_column('G1:G1', 8)
        worksheet.set_column('H1:H1', 8)
        worksheet.set_column('I1:I1', 8)
        worksheet.set_column('J1:J1', 8)
        worksheet.set_column('K1:K1', 8)
        worksheet.set_column('L1:K1', 8)
        worksheet.set_column('M1:M1', 8)

        i = 9
        count = 1
        for record in lines.line_ids:
            worksheet.write(i, 0, tools.ustr(record.objective if record.objective else ''), normal_format)
            worksheet.write(i, 1, tools.ustr(dict(self.env['enterprise_mgm_sys.ctrl_measures_efficacy_line'].fields_get(allfields=['compliance'])['compliance']['selection'])[record.compliance]), normal_center_format)
            worksheet.write(i, 2, tools.ustr(record.risk_id.name if record.risk_id.name else ''), normal_format)
            worksheet.write(i, 3, tools.ustr(dict(self.env['enterprise_mgm_sys.ctrl_measures_efficacy_line'].fields_get(allfields=['probability'])['probability']['selection'])[record.probability]), normal_center_format)
            worksheet.write(i, 4, tools.ustr(dict(self.env['enterprise_mgm_sys.ctrl_measures_efficacy_line'].fields_get(allfields=['consequence'])['consequence']['selection'])[record.consequence]), normal_center_format)
            worksheet.write(i, 5, tools.ustr(dict(self.env['enterprise_mgm_sys.ctrl_measures_efficacy_line'].fields_get(allfields=['level'])['level']['selection'])[record.level]), normal_center_format)
            worksheet.write(i, 6, tools.ustr(record.measures if record.measures else ''), normal_format)
            worksheet.write(i, 7, tools.ustr(record.compliance_dates if record.compliance_dates else ''), normal_center_format)
            worksheet.write(i, 8, tools.ustr(record.employee_id.name if record.employee_id.name else ''), normal_center_format)
            worksheet.write(i, 9, tools.ustr(dict(self.env['enterprise_mgm_sys.ctrl_measures_efficacy_line'].fields_get(allfields=['new_probability'])['new_probability']['selection'])[record.new_probability]), normal_center_format)
            worksheet.write(i, 10, tools.ustr(dict(self.env['enterprise_mgm_sys.ctrl_measures_efficacy_line'].fields_get(allfields=['new_consequence'])['new_consequence']['selection'])[record.new_consequence]), normal_center_format)
            worksheet.write(i, 11, tools.ustr(dict(self.env['enterprise_mgm_sys.ctrl_measures_efficacy_line'].fields_get(allfields=['new_level'])['new_level']['selection'])[record.new_level]), normal_center_format)
            worksheet.write(i, 12, tools.ustr(self.calc_efficacy(record)), normal_center_format)
            i += 1

        worksheet.merge_range(i + 1, 0, i + 1, 12, tools.ustr('LEYENDA:'), normal_format_no_border)
        worksheet.merge_range(i + 2, 0, i + 2, 12, tools.ustr('Cuando el valor de la evaluación del riesgo actual es menor o igual a la evaluación inicial del riesgo se evalúa de eficaz la medida, cuando es mayor se evalúa no eficaz.'), normal_format_no_border)
        worksheet.set_row(i + 1, 25)
        worksheet.set_row(i + 2, 25)

    def calc_efficacy(self, record):
        levels = {
            'trivial': 0,
            'acceptable': 1,
            'moderate': 2,
            'important': 3,
        }
        if levels[record.level] >= levels[record.new_level]:
            return 'Eficaz'
        else:
            return 'No Eficaz'


ControlMeasuresEfficacy('report.enterprise_mgm_sys.control_measures_efficacy_report', 'enterprise_mgm_sys.control_measures_efficacy')

