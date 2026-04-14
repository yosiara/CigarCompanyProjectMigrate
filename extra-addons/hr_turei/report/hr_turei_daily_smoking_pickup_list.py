# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class HrTureiDailySmokingPickUpList(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet(tools.ustr('Listado'))
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11})
        merge_format.set_text_wrap()
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 10})
        normal_format.set_text_wrap()
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
        worksheet.merge_range('C1:E3', tools.ustr('Relación de trabajadores que recogen fuma diaria'), merge_format)
        worksheet.merge_range('A1:B3', tools.ustr(''), merge_format)
        worksheet.merge_range('F1:G1', tools.ustr('Versión: 00'), identification_format)
        worksheet.merge_range('F2:G2', tools.ustr('Fecha: 01/08/2018'), identification_format)
        worksheet.merge_range('F3:G3', tools.ustr('Código : PE-DCH-02-R-06'), identification_format)
        worksheet.merge_range('B4:B5', tools.ustr('Área a la que pertenece'), merge_format)
        worksheet.merge_range('C4:G4', tools.ustr('Nombres y Apellidos'), merge_format)
        worksheet.write('C5', tools.ustr('Recoge'), merge_format)
        worksheet.write('D5', tools.ustr('Firma'), merge_format)
        worksheet.merge_range('E5:F5', tools.ustr('Sustituto'), merge_format)
        worksheet.write('G5', tools.ustr('Firma'), merge_format)

        worksheet.set_column('A1:A1', 12)
        worksheet.set_column('B1:B1', 15)
        worksheet.set_column('C1:C1', 25)
        worksheet.set_column('D1:D1', 8)
        worksheet.set_column('E1:E1', 12)
        worksheet.set_column('F1:F1', 13)
        worksheet.set_column('G1:G1', 8)
        daily_smoking = self.env['hr_turei.daily_smoking'].search([('company_id', '=', lines.company_id.id)])

        i = 5
        for record in daily_smoking:
            if record.external_staff:
                worksheet.write(i, 1, tools.ustr(record.external_area_id.name), normal_format)
                worksheet.write(i, 2, tools.ustr(record.external_area_pick_up.name), normal_format)
                worksheet.merge_range(i, 4, i, 5, tools.ustr(record.external_area_pick_up_sub.name), normal_format)
                worksheet.write_blank(i, 3, 1, normal_center_format)
                worksheet.write_blank(i, 6, 1, normal_center_format)
            else:
                worksheet.write(i, 1, tools.ustr(record.department_id.name), normal_format)
                worksheet.write(i, 2, tools.ustr(record.pick_up.name), normal_format)
                worksheet.merge_range(i, 4, i, 5, tools.ustr(record.pick_up_sub.name), normal_format)
                worksheet.write_blank(i, 3, 1, normal_center_format)
                worksheet.write_blank(i, 6, 1, normal_center_format)
            i += 1

        worksheet.merge_range(3, 0, i - 1, 0, tools.ustr(lines.company_id.name), merge_format)

        worksheet.merge_range(i + 3, 0, i + 3, 2, 'Elaborado por: %s' % tools.ustr(lines.elaborated_by.name),
                              sign_format)
        worksheet.merge_range(i + 4, 0, i + 4, 2, 'Cargo: %s' % tools.ustr(lines.elaborated_by.job_id.name),
                              sign_format)
        worksheet.merge_range(i + 3, 3, i + 3, 6, 'Revisado por: %s' % tools.ustr(lines.approved_by.name), sign_format)
        worksheet.merge_range(i + 4, 3, i + 4, 6, 'Cargo: %s' % tools.ustr(lines.approved_by.job_id.name), sign_format)


HrTureiDailySmokingPickUpList('report.hr_turei.daily_smoking_pickup_list', 'hr_turei.daily_smoking_pickup_wzd')
