# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ControlComplianceMeasures(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet(tools.ustr('R5'))
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
            'addons_path'] + '/enterprise_mgm_sys/static/src/img/logo-landscape.jpg',
                               {'x_offset': 15, 'y_offset': 2, 'x_scale': 1.2, 'y_scale': 1.5})
        worksheet.merge_range('C1:N3', tools.ustr('Control del cumplimiento de las medidas del Plan de Prevención de Riesgos (R-5)'), merge_format)
        worksheet.merge_range('A1:B3', tools.ustr(''), merge_format)
        worksheet.merge_range('O1:R1', tools.ustr('Versión: 00'), identification_format)
        worksheet.merge_range('O2:R2', tools.ustr('Fecha de aprobación: 21/6/2018'), identification_format)
        worksheet.merge_range('O3:R3', tools.ustr('Código: M-DTD-03-R19'), identification_format)

        worksheet.merge_range('A7:A8', tools.ustr('No'), merge_format)
        worksheet.merge_range('B7:B8', tools.ustr('Medidas'), merge_format)
        worksheet.merge_range('C7:C8', tools.ustr('Responsable'), merge_format)
        worksheet.merge_range('D7:D8', tools.ustr('Ejecutan'), merge_format)
        worksheet.merge_range('E7:E8', tools.ustr('F/C'), merge_format)
        worksheet.merge_range('F7:R7', tools.ustr('Firma del personal que ejecuta la acción'), merge_format)
        worksheet.write('F8', tools.ustr('E'), merge_format)
        worksheet.write('G8', tools.ustr('F'), merge_format)
        worksheet.write('H8', tools.ustr('M'), merge_format)
        worksheet.write('I8', tools.ustr('A'), merge_format)
        worksheet.write('J8', tools.ustr('M'), merge_format)
        worksheet.write('K8', tools.ustr('J'), merge_format)
        worksheet.write('L8', tools.ustr('J'), merge_format)
        worksheet.write('M8', tools.ustr('A'), merge_format)
        worksheet.write('N8', tools.ustr('S'), merge_format)
        worksheet.write('O8', tools.ustr('O'), merge_format)
        worksheet.write('P8', tools.ustr('N'), merge_format)
        worksheet.write('Q8', tools.ustr('D'), merge_format)
        worksheet.write('R8', tools.ustr('Observaciones'), merge_format)

        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 22)
        worksheet.set_column('C1:C1', 18)
        worksheet.set_column('D1:D1', 18)
        worksheet.set_column('E1:E1', 10)
        worksheet.set_column('F1:F1', 8)
        worksheet.set_column('G1:G1', 8)
        worksheet.set_column('H1:H1', 8)
        worksheet.set_column('I1:I1', 8)
        worksheet.set_column('J1:J1', 8)
        worksheet.set_column('K1:K1', 8)
        worksheet.set_column('L1:L1', 8)
        worksheet.set_column('M1:M1', 8)
        worksheet.set_column('N1:N1', 8)
        worksheet.set_column('O1:O1', 8)
        worksheet.set_column('P1:P1', 8)
        worksheet.set_column('Q1:Q1', 8)
        worksheet.set_column('R1:R1', 10)

        i = 8
        count = 1
        for record in lines.measure_ids:
            worksheet.write(i, 0, tools.ustr(count), merge_format)
            worksheet.write(i, 1, tools.ustr(record.measures if record.measures else ''), merge_format)
            worksheet.write(i, 2, tools.ustr(record.employee_id.name if record.employee_id.name else ''), merge_format)
            worksheet.write(i, 3, tools.ustr(record.execute if record.execute else ''), merge_format)
            worksheet.write(i, 4, tools.ustr(record.compliance_dates if record.compliance_dates else ''), merge_format)
            worksheet.write(i, 5, tools.ustr(''), merge_format)
            worksheet.write(i, 6, tools.ustr(''), merge_format)
            worksheet.write(i, 7, tools.ustr(''), merge_format)
            worksheet.write(i, 8, tools.ustr(''), merge_format)
            worksheet.write(i, 9, tools.ustr(''), merge_format)
            worksheet.write(i, 10, tools.ustr(''), merge_format)
            worksheet.write(i, 11, tools.ustr(''), merge_format)
            worksheet.write(i, 12, tools.ustr(''), merge_format)
            worksheet.write(i, 13, tools.ustr(''), merge_format)
            worksheet.write(i, 14, tools.ustr(''), merge_format)
            worksheet.write(i, 15, tools.ustr(''), merge_format)
            worksheet.write(i, 16, tools.ustr(''), merge_format)
            worksheet.write(i, 17, tools.ustr(''), merge_format)
            i += 1
            count += 1


ControlComplianceMeasures('report.enterprise_mgm_sys.control_compliance_measures_report', 'enterprise_mgm_sys.risks_prevention_plan')
