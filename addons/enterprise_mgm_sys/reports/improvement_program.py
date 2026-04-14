# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ImprovementProgram(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet(tools.ustr('Mejoras'))
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

        worksheet.insert_image('B2', addons_manifest['hr_turei'][
            'addons_path'] + '/enterprise_mgm_sys/static/src/img/logo-landscape.jpg',
                               {'x_offset': 15, 'y_offset': 5, 'x_scale': 1.2, 'y_scale': 1.2})
        worksheet.merge_range('E2:G2', tools.ustr('PROGRAMA DE MEJORA  DEL SISTEMA DE DIRECCIÓN Y GESTIÓN EMPRESARIAL %s') % lines.year, merge_format)
        worksheet.merge_range('B2:D2', tools.ustr(''), merge_format)
        worksheet.write('H2', tools.ustr(''), merge_format)
        worksheet.insert_image('H2', addons_manifest['hr_turei'][
            'addons_path'] + '/enterprise_mgm_sys/static/src/img/cert.png',
                               {'x_offset': 90, 'y_offset': 5, 'x_scale': 0.7, 'y_scale': 0.7})

        worksheet.write('B3', tools.ustr('No'), merge_format)
        worksheet.write('C3', tools.ustr('Área'), merge_format)
        worksheet.write('D3', tools.ustr('Sistema'), merge_format)
        worksheet.write('E3', tools.ustr('Acción'), merge_format)
        worksheet.write('F3', tools.ustr('Fecha de Cumplimiento'), merge_format)
        worksheet.write('G3', tools.ustr('Ejecuta'), merge_format)
        worksheet.write('H3', tools.ustr('Participa '), merge_format)

        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 8)
        worksheet.set_column('C1:C1', 10)
        worksheet.set_column('D1:D1', 18)
        worksheet.set_column('E1:E1', 50)
        worksheet.set_column('F1:F1', 18)
        worksheet.set_column('G1:G1', 30)
        worksheet.set_column('H1:H1', 30)
        worksheet.set_row(1, 40)
        i = 3
        count = 1
        for record in lines.action_ids:
            worksheet.write(i, 1, tools.ustr(count), normal_center_format)
            worksheet.write(i, 2, tools.ustr(record.area.name if record.area else ''), normal_center_format)
            worksheet.write(i, 3, tools.ustr(record.system_id.name if record.system_id.name else ''), normal_center_format)
            worksheet.write(i, 4, tools.ustr(record.name if record.name else ''), normal_format)
            worksheet.write(i, 5, tools.ustr(record.compliance_date if record.compliance_date else ''), normal_center_format)
            worksheet.write(i, 6, tools.ustr(record.execute_id.name if record.execute_id.name else ''), normal_format)
            worksheet.write(i, 7, tools.ustr(self._get_participate(record)), normal_format)
            i += 1
            count += 1

        bold = workbook.add_format({'bold': True})
        left_right = workbook.add_format({'left': 1, 'right': 1})
        worksheet.merge_range(i, 1, i, 7, '', left_right)
        worksheet.merge_range(i + 1, 1, i + 1, 7, '', left_right)
        worksheet.write_rich_string(i + 1, 1, bold, tools.ustr('Aprobado por: '), lines.approve_id.name, left_right)
        normal_format_no_top = workbook.add_format(
            {'bold': 0, 'left': 1, 'right': 1, 'bottom': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 11})
        normal_format_no_top.set_text_wrap()
        worksheet.merge_range(i + 2, 1, i + 2, 7, tools.ustr(lines.approve_id.job_id.name), normal_format_no_top)

    def _get_participate(self, line):
        if line.participate_use_employees:
            participate = ''
            for employee in line.participate_ids:
                    participate += employee.name + ', '
            return participate
        else:
            return line.participate if line.participate else ''


ImprovementProgram('report.enterprise_mgm_sys.improvement_program_report', 'enterprise_mgm_sys.improvement_program')
