# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class HrTureiDailySmokingList(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Listado'))
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11})
        merge_format.set_text_wrap()
        merge_format_no_border = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 11})
        merge_format_no_border.set_text_wrap()
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
            {'bold': 0, 'right': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        identification_format_top = workbook.add_format(
            {'bold': 0, 'top': 1, 'right': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        identification_format_bottom = workbook.add_format(
            {'bold': 0, 'bottom': 1, 'right': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        worksheet.insert_image('A1', addons_manifest['hr_turei'][
            'addons_path'] + '/hr_turei/static/src/img/logo-landscape.jpg',
                               {'x_offset': 15, 'y_offset': 5, 'x_scale': 1.5, 'y_scale': 1.5})
        worksheet.merge_range('D1:G3', tools.ustr('Relación de trabajadores que reciben fuma diaria'), merge_format)
        worksheet.merge_range('A1:C3', tools.ustr(''), merge_format)
        worksheet.merge_range('H1:I1', tools.ustr('Versión: 00'), identification_format_top)
        worksheet.merge_range('H2:I2', tools.ustr('Fecha: 01/08/2018'), identification_format)
        worksheet.merge_range('H3:I3', tools.ustr('Código : PE-DCH-02-R-05'), identification_format_bottom)
        worksheet.merge_range('A4:I4', tools.ustr('Correspondiente a: (%s)' % datetime.strptime(lines.date, DEFAULT_SERVER_DATE_FORMAT).date().strftime('%d/%m/%Y')), merge_format)
        worksheet.merge_range('B5:B6', tools.ustr('Área a la que pertenece'), merge_format)
        worksheet.merge_range('C5:C6', tools.ustr('Código'), merge_format)
        worksheet.merge_range('D5:D6', tools.ustr('Turno'), merge_format)
        worksheet.merge_range('E5:E6', tools.ustr('Nombres y Apellidos'), merge_format)
        worksheet.merge_range('F5:G5', tools.ustr('Área'), merge_format)
        worksheet.write('F6', tools.ustr('I'), merge_format)
        worksheet.write('G6', tools.ustr('E'), merge_format)
        worksheet.merge_range('H5:I5', tools.ustr('Cigarrillos'), merge_format)
        worksheet.write('H6', tools.ustr('Criollos'), merge_format)
        worksheet.write('I6', tools.ustr('Aromas'), merge_format)
        worksheet.set_column('A1:A1', 12)
        worksheet.set_column('B1:B1', 15)
        worksheet.set_column('C1:C1', 8)
        worksheet.set_column('D1:D1', 10)
        worksheet.set_column('E1:E1', 25)
        worksheet.set_column('F1:F1', 5)
        worksheet.set_column('G1:G1', 5)
        worksheet.set_column('H1:H1', 8)
        worksheet.set_column('I1:I1', 8)
        worksheet.repeat_rows(0,3)
        departments = self.env['hr.department'].search([('company_id', '=', lines.company_id.id)])
        areas = self.env['hr_turei.external_area'].search(
            [('company_id', '=', lines.company_id.id), ('carries_daily_smoking', '=', True)])

        i = 6
        for department in departments:
            row_start_depart = i
            ids = self.env['hr_turei.employee_movement'].read_group(
                domain=[('new_job_position_id.department_id', '=', department.id), '|', '&',
                        ('movement_start_date', '<=', lines.date), ('movement_end_date', '>=', lines.date), '&',
                        ('movement_start_date', '<=', lines.date), ('movement_end_date', '=', False)],
                fields=['employee_id'], groupby=['employee_id'])
            ids = map(lambda x: x['employee_id'][0], ids)
            members = self.env['hr.employee'].search([('id', 'in', ids)])
            for employee in members:
                working = self._is_working(employee.calendar_id, lines.date)
                if working and employee.carries_daily_smoking:
                    worksheet.write(i, 2, tools.ustr(employee.code), normal_center_format)
                    worksheet.write(i, 3, tools.ustr(employee.calendar_id.name), normal_format)
                    worksheet.write(i, 4, tools.ustr(employee.name), normal_format)
                    if department.smoking_type == 'internal':
                        worksheet.write_number(i, 5, 1, normal_center_format)
                        worksheet.write_number(i, 6, 0, normal_center_format)
                    else:
                        worksheet.write_number(i, 6, 1, normal_center_format)
                        worksheet.write_number(i, 5, 0, normal_center_format)

                    if employee.brand_smoke_id and 'Aroma' in employee.brand_smoke_id.sgp_name:
                        worksheet.write_number(i, 8, int(employee.packs_amount), normal_center_format)
                        worksheet.write_number(i, 7, 0, normal_center_format)
                    else:
                        worksheet.write_number(i, 7, int(employee.packs_amount), normal_center_format)
                        worksheet.write_number(i, 8, 0, normal_center_format)
                    i += 1
            if i > row_start_depart:
                if row_start_depart == i - 1:
                    worksheet.write(row_start_depart, 1, tools.ustr(department.name), normal_format)
                else:
                    worksheet.merge_range(row_start_depart, 1, i - 1, 1, tools.ustr(department.name), normal_format)

        for area in areas:
            row_start_area = i
            for person in area.external_staff_ids:
                working = self._is_working(person.calendar_id, lines.date)
                if working and person.carries_daily_smoking:
                    worksheet.write(i, 2, tools.ustr(person.code), normal_center_format)
                    worksheet.write_blank(i, 3, '', normal_format)
                    worksheet.write(i, 4, tools.ustr(person.name), normal_format)
                    if area.smoking_type == 'internal':
                        worksheet.write_number(i, 5, 1, normal_center_format)
                        worksheet.write_number(i, 6, 0, normal_center_format)
                    else:
                        worksheet.write_number(i, 6, 1, normal_center_format)
                        worksheet.write_number(i, 5, 0, normal_center_format)

                    if person.brand_smoke_id and 'Aroma' in person.brand_smoke_id.sgp_name:
                        worksheet.write_number(i, 8, int(person.packs_amount), normal_center_format)
                        worksheet.write_number(i, 7, 0, normal_center_format)
                    else:
                        worksheet.write_number(i, 7, int(person.packs_amount), normal_center_format)
                        worksheet.write_number(i, 8, 0, normal_center_format)
                    i += 1
            if i > row_start_area:
                if row_start_depart == i - 1:
                    worksheet.write(row_start_area, 1, tools.ustr(area.name), normal_format)
                else:
                    worksheet.merge_range(row_start_area, 1, i - 1, 1, tools.ustr(area.name), normal_format)

        worksheet.write(i, 1, 'TOTAL', merge_format)
        worksheet.write_blank(i, 2, 1, normal_center_format)
        worksheet.write_blank(i, 3, 1, normal_center_format)
        worksheet.write_blank(i, 4, 1, normal_center_format)
        worksheet.write_formula(i, 5, 'SUM(F7:F%s)' % str(i), normal_center_format)
        worksheet.write_formula(i, 6, 'SUM(G7:G%s)' % str(i), normal_center_format)
        worksheet.write_formula(i, 7, 'SUM(H7:H%s)' % str(i), normal_center_format)
        worksheet.write_formula(i, 8, 'SUM(I7:I%s)' % str(i), normal_center_format)
        worksheet.merge_range(4, 0, i, 0, tools.ustr(lines.company_id.name), merge_format)

        worksheet.merge_range(i + 3, 0, i + 3, 3, 'Elaborado por: %s' % tools.ustr(lines.elaborated_by.name), sign_format)
        worksheet.merge_range(i + 4, 0, i + 4, 3, 'Cargo: %s' % tools.ustr(lines.elaborated_by.job_id.name), sign_format)
        worksheet.merge_range(i + 3, 4, i + 3, 8, 'Revisado por: %s' % tools.ustr(lines.approved_by.name), sign_format)
        worksheet.merge_range(i + 4, 4, i + 4, 8, 'Cargo: %s' % tools.ustr(lines.approved_by.job_id.name), sign_format)

    def _is_working(self, calendar, date):
        working = False
        if calendar:
            hours = calendar.get_working_hours_of_date(fields.Datetime.from_string(date))
            if hours >= 8.0 or 5.0 == hours:
                working = True
        return working

HrTureiDailySmokingList('report.hr_turei.daily_smoking_list', 'hr_turei.daily_smoking_wzd')
