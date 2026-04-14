# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class OrdersPlannedReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Resumen de Órdenes Planificadas'))
        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})

        work_order = self.env['turei_maintenance.work_order'].search(
            [('opening_date', '>=', lines.date_start), ('opening_date', '<=', lines.date_end), ('cycle_id', '!=', False)], order='closing_date')

        worksheet.merge_range('A1:H1', tools.ustr("Resumen de Órdenes Planificadas desde: %s  hasta: %s") %(lines.date_start, lines.date_end), head_format)

        worksheet.write('A2', tools.ustr('No.'), merge_format)
        worksheet.write('B2', tools.ustr('No. Inventario'), merge_format)
        worksheet.write('C2', tools.ustr('Nombre del Equipo'), merge_format)
        worksheet.write('D2', tools.ustr('STP'), merge_format)
        worksheet.write('E2', tools.ustr('F_PL'), merge_format)
        worksheet.write('F2', tools.ustr('Taller'), merge_format)
        worksheet.write('G2', tools.ustr('Línea'), merge_format)
        worksheet.write('H2', tools.ustr('No. OT'), merge_format)

        x = 2
        c = 1
        for wk in work_order:
            worksheet.write(x, 0, c, normal_format)
            worksheet.write(x, 1, wk.equipament_id.code, normal_format)
            worksheet.write(x, 2, wk.equipament_id.name, normal_format)
            worksheet.write(x, 3, wk.cycle_id.cycle, normal_format)
            worksheet.write(x, 4, wk.opening_date, normal_format)
            worksheet.write(x, 5, wk.equipament_id.category_id.name, normal_format)
            worksheet.write(x, 6, wk.equipament_id.line_id.name, normal_format)
            worksheet.write(x, 7, wk.number_new, normal_format)
            c += 1
            x += 1

OrdersPlannedReport('report.turei_maintenance.orders_planned_report', 'wzd.orders.planned')
