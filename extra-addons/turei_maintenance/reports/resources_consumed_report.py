# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ResourcesConsumedReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Recursos Consumidos'))
        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})

        domain = [('opening_date', '>=', lines.date_start), ('opening_date', '<=', lines.date_end)]
        if lines.equipment_id:
            domain.append(('equipament_id', '=', lines.equipment_id.id))
        if lines.category_id:
            domain.append(('category_id', '=', lines.category_id.id))

        work_order = self.env['turei_maintenance.work_order'].search(domain, order='opening_date')

        worksheet.merge_range('A1:M1', tools.ustr("Recursos Consumidos por Órdenes de Trabajo desde: %s - hasta: %s") %(lines.date_start, lines.date_end), head_format)
        worksheet.write('A2', tools.ustr('No.'), merge_format)
        worksheet.write('B2', tools.ustr('Fecha'), merge_format)
        worksheet.write('C2', tools.ustr('Código'), merge_format)
        worksheet.write('D2', tools.ustr('Descripción'), merge_format)
        worksheet.write('E2', tools.ustr('UM'), merge_format)
        worksheet.write('F2', tools.ustr('Existencia'), merge_format)
        worksheet.write('G2', tools.ustr('Cantidad'), merge_format)
        worksheet.write('H2', tools.ustr('Importe CUP'), merge_format)
        worksheet.write('I2', tools.ustr('Código Almacén'), merge_format)
        worksheet.write('J2', tools.ustr('Almacén'), merge_format)
        worksheet.write('K2', tools.ustr('Código Centro de Costo'), merge_format)
        worksheet.write('L2', tools.ustr('Centro de Costo'), merge_format)
        worksheet.write('M2', tools.ustr('Estado'), merge_format)
        worksheet.write('N2', tools.ustr('No. Orden'), merge_format)
        # worksheet.write('O2', tools.ustr('Equipo'), merge_format)
        # worksheet.write('P2', tools.ustr('Taller'), merge_format)

        x = 2
        c = 1
        for wk in work_order:
            for p in wk.product_order_ids:
                worksheet.write(x, 0, c, normal_format)
                worksheet.write(x, 1, wk.opening_date, normal_format)
                worksheet.write(x, 2, p.product_id.code, normal_format)
                worksheet.write(x, 3, p.product_id.name, normal_format)
                worksheet.write(x, 4, p.product_id.uom_id.name, normal_format)
                worksheet.write(x, 5, p.product_id.total, normal_format)
                worksheet.write(x, 6, p.quantity, normal_format)
                worksheet.write(x, 7, round(p.product_id.price * p.quantity,2), normal_format)
                worksheet.write(x, 8, tools.ustr(p.product_id.location_ids[0].warehouse_id.code), normal_format)
                worksheet.write(x, 9, tools.ustr(p.product_id.location_ids[0].warehouse_id.name), normal_format)
                worksheet.write(x, 10, wk.receive_cost_center_id.code, normal_format)
                worksheet.write(x, 11, wk.receive_cost_center_id.name, normal_format)
                worksheet.write(x, 12, "Cerrada" if wk.state == 'closed' else "Abierta", normal_format)
                worksheet.write(x, 13, wk.number_new, normal_format)
                # worksheet.write(x, 14, wk.equipament_id.name + "-" + wk.equipament_id.code, normal_format)
                # worksheet.write(x, 15, wk.category_id.name, normal_format)
                c += 1
                x += 1

ResourcesConsumedReport('report.turei_maintenance.resources_consumed_report', 'wzd.resources.consumed')
