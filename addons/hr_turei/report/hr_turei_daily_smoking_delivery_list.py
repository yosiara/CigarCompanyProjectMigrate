# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class HrTureiDailySmokingDeliveryList(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet(tools.ustr('Listado'))
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format.set_text_wrap()
        merge_format_normal = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format_normal.set_text_wrap()
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
        identification_format_top = workbook.add_format(
            {'bold': 0, 'top': 1, 'right': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        identification_format = workbook.add_format(
            {'bold': 0, 'right': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        identification_format_bottom = workbook.add_format(
            {'bold': 0, 'bottom': 1, 'right': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        worksheet.insert_image('A1', addons_manifest['hr_turei'][
            'addons_path'] + '/hr_turei/static/src/img/logo-landscape.jpg',
                               {'x_offset': 15, 'y_offset': 2, 'x_scale': 1.2, 'y_scale': 1.5})
        worksheet.merge_range('C1:J3', tools.ustr('Registro de entrega de fuma diaria'), merge_format)
        worksheet.merge_range('A1:B3', tools.ustr(''), merge_format_normal)
        worksheet.merge_range('K1:L1', tools.ustr('Versión: 00'), identification_format_top)
        worksheet.merge_range('K2:L2', tools.ustr('Fecha: 01/08/2018'), identification_format)
        worksheet.merge_range('K3:L3', tools.ustr('Código : PE-DCH-02-R-07'), identification_format_bottom)
        worksheet.merge_range('A4:L4', tools.ustr('Fecha: (%s)' % datetime.strptime(lines.date, DEFAULT_SERVER_DATE_FORMAT).date().strftime('%d/%m/%Y')), merge_format_normal)
        worksheet.merge_range('A5:B6', tools.ustr('Área'), merge_format_normal)
        worksheet.merge_range('D5:F5', tools.ustr('Cantidad'), merge_format_normal)
        worksheet.merge_range('G5:J5', '', merge_format_normal)
        worksheet.merge_range('C5:C6', tools.ustr('U'), merge_format_normal)
        worksheet.write_blank('K5', '', merge_format_normal)
        worksheet.write_blank('L5', '', merge_format_normal)
        worksheet.write('D6', tools.ustr('Asig'), merge_format_normal)
        worksheet.write('E6', tools.ustr('Criollos'), merge_format_normal)
        worksheet.write('F6', tools.ustr('Aromas'), merge_format_normal)
        worksheet.write('G6', tools.ustr('Asig'), merge_format_normal)
        worksheet.write('H6', tools.ustr('Criollos'), merge_format_normal)
        worksheet.write('I6', tools.ustr('Aromas'), merge_format_normal)
        worksheet.write('J6', tools.ustr('Total'), merge_format_normal)
        worksheet.write('K6', tools.ustr('Nombre y Apellidos'), merge_format_normal)
        worksheet.write('L6', tools.ustr('Firmas'), merge_format_normal)

        worksheet.set_column('A1:A1', 15)
        worksheet.set_column('B1:B1', 25)
        worksheet.set_column('C1:C1', 5)
        worksheet.set_column('D1:D1', 6)
        worksheet.set_column('E1:E1', 7)
        worksheet.set_column('F1:F1', 7)
        worksheet.set_column('G1:G1', 6)
        worksheet.set_column('H1:H1', 7)
        worksheet.set_column('I1:I1', 7)
        worksheet.set_column('J1:J1', 6)
        worksheet.set_column('K1:K1', 15)
        worksheet.set_column('L1:L1', 10)

        total_aromas = 0
        total_criollos = 0
        i = 6
        for record in lines.company_id:
            row_start_company = i
            areas = self.env['hr_turei.daily_smoking'].search([('company_id', '=', record.id)])
            for area in areas:
                worksheet.write(i, 1, tools.ustr(area.area), normal_format)
                worksheet.write(i, 2, tools.ustr('Cjt'), normal_center_format)
                if area.external_staff:
                    members = self.env['hr_turei.external_staff'].search([('area_id', '=', area.external_area_id.id)])
                else:
                    ids = self.env['hr_turei.employee_movement'].read_group(domain=[('new_job_position_id.department_id', '=', area.department_id.id), '|', '&', ('movement_start_date', '<=', lines.date), ('movement_end_date', '>=', lines.date), '&', ('movement_start_date', '<=', lines.date), ('movement_end_date', '=', False)], fields=['employee_id'], groupby=['employee_id'])
                    ids = map(lambda x: x['employee_id'][0], ids)
                    members = self.env['hr.employee'].search([('id', 'in', ids)])

                criollos = 0
                aromas = 0
                for member in members:
                    working = self._is_working(member.calendar_id, lines.date)
                    if working and member.carries_daily_smoking:
                        if member.brand_smoke_id and 'Aroma' in member.brand_smoke_id.sgp_name:
                            aromas += int(member.packs_amount)
                        elif member.carries_daily_smoking:
                            criollos += int(member.packs_amount)

                total_aromas += aromas
                total_criollos += criollos

                worksheet.write_number(i, 3, criollos + aromas, normal_center_format)
                worksheet.write_number(i, 4, criollos, normal_center_format)
                worksheet.write_number(i, 5, aromas, normal_center_format)
                worksheet.write_blank(i, 6, 1, normal_center_format)
                worksheet.write_blank(i, 7, 1, normal_center_format)
                worksheet.write_blank(i, 8, 1, normal_center_format)
                worksheet.write_blank(i, 9, 1, normal_center_format)
                worksheet.write_blank(i, 10, 1, normal_center_format)
                worksheet.write_blank(i, 11, 1, normal_center_format)
                i += 1

            if i > row_start_company:
                worksheet.write(i, 1, tools.ustr('Total %s' % area.area), merge_format)
                worksheet.write(i, 2, tools.ustr('Cjt'), normal_center_format)
                worksheet.write_formula(i, 3, 'SUM(D%s:D%s)' % (row_start_company + 1, i), normal_center_format)
                worksheet.write_formula(i, 4, 'SUM(E%s:E%s)' % (row_start_company + 1, i), normal_center_format)
                worksheet.write_formula(i, 5, 'SUM(F%s:F%s)' % (row_start_company + 1, i), normal_center_format)
                worksheet.write_blank(i, 6, 1, normal_center_format)
                worksheet.write_blank(i, 7, 1, normal_center_format)
                worksheet.write_blank(i, 8, 1, normal_center_format)
                worksheet.write_blank(i, 9, 1, normal_center_format)
                worksheet.write_blank(i, 10, 1, normal_center_format)
                worksheet.write_blank(i, 11, 1, normal_center_format)
                i += 1
                if row_start_company == i - 1:
                    worksheet.write(row_start_company, 0, tools.ustr(record.name), normal_center_format)
                else:
                    worksheet.merge_range(row_start_company, 0, i - 1, 0, tools.ustr(record.name), normal_center_format)

        worksheet.merge_range(i, 0, i, 1, tools.ustr('Total general'), merge_format)
        worksheet.write(i, 2, tools.ustr('Cjt'), normal_center_format)
        worksheet.write_number(i, 3, total_criollos + total_aromas, normal_center_format)
        worksheet.write_number(i, 4, total_criollos, normal_center_format)
        worksheet.write_number(i, 5, total_aromas, normal_center_format)
        worksheet.write_blank(i, 6, 1, normal_center_format)
        worksheet.write_blank(i, 7, 1, normal_center_format)
        worksheet.write_blank(i, 8, 1, normal_center_format)
        worksheet.write_blank(i, 9, 1, normal_center_format)
        worksheet.write_blank(i, 10, 1, normal_center_format)
        worksheet.write_blank(i, 11, 1, normal_center_format)

    def _is_working(self, calendar, date):
        working = False
        if calendar:
            hours = calendar.get_working_hours_of_date(fields.Datetime.from_string(date))
            if hours >= 8.0 or 5.0 == hours:
                working = True
        return working

HrTureiDailySmokingDeliveryList('report.hr_turei.daily_smoking_delivery_list', 'hr_turei.daily_smoking_delivery_wzd')
