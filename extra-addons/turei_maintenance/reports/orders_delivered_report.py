# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class OrdersDeliveredReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Resumen de órdenes entregadas'))
        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})

        work_order = self.env['turei_maintenance.work_order'].search(
            [('closing_date', '>=', lines.date_start), ('closing_date', '<=', lines.date_end), ('delivered', '=', True)], order='closing_date')

        worksheet.merge_range('A1:G1', tools.ustr("Resumen de Órdenes Entregadas desde: %s hasta: %s") %(lines.date_start, lines.date_end), head_format)
        worksheet.write('A2', tools.ustr('No.OT'), merge_format)
        worksheet.write('B2', tools.ustr('Fecha de Apertura'), merge_format)
        worksheet.write('C2', tools.ustr('Emisor'), merge_format)
        worksheet.write('D2', tools.ustr('Ejecutor'), merge_format)
        worksheet.write('E2', tools.ustr('Código'), merge_format)
        worksheet.write('F2', tools.ustr('Máquina o Área'), merge_format)
        worksheet.write('G2', tools.ustr('CC según OT'), merge_format)

        x = 2
        for wk in work_order:
            worksheet.write(x, 0, wk.number_new, normal_format)
            worksheet.write(x, 1, wk.opening_date, normal_format)
            worksheet.write(x, 2, wk.emitter_id.name, normal_format)
            worksheet.write(x, 3, wk.executor_id.name, normal_format)
            worksheet.write(x, 4, wk.equipament_id.code, normal_format)
            worksheet.write(x, 5, wk.equipament_id.name, normal_format)
            worksheet.write(x, 6, wk.receive_cost_center_id.code, normal_format)
            x += 1

OrdersDeliveredReport('report.turei_maintenance.orders_delivered_report', 'wzd.orders.delivered')
