# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class OrdersPendingReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Resumen de Órdenes Pendientes'))
        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})

        today = datetime.today().date()
        today = today.replace(day=1, month=1)

        work_order = self.env['turei_maintenance.work_order'].search(
            [('opening_date', '>=', today.strftime('%Y-%m-%d')),('opening_date', '<=', lines.date_end),('state', '=', 'open')], order='opening_date')

        worksheet.merge_range('A1:H1', tools.ustr("Resumen de Órdenes Pendientes con Fecha de Cierre: %s") %(lines.date_end), head_format)

        worksheet.write('A2', tools.ustr('Emisor'), merge_format)
        worksheet.write('B2', tools.ustr('No. OT'), merge_format)
        worksheet.write('C2', tools.ustr('Código'), merge_format)
        worksheet.write('D2', tools.ustr('Máquina o Área'), merge_format)
        worksheet.write('E2', tools.ustr('Tipo de Trabajo'), merge_format)
        worksheet.write('F2', tools.ustr('Ejecutor'), merge_format)
        worksheet.write('G2', tools.ustr('Fecha Apertura'), merge_format)
        worksheet.write('H2', tools.ustr('Estado'), merge_format)
        worksheet.write('I2', tools.ustr('Total'), merge_format)
        dicc_emisor = {}
        for wk in work_order:
            dic_line = {}
            dic_line['number'] = wk.number_new
            dic_line['code'] = wk.equipament_id.code
            dic_line['equipment'] = wk.equipament_id.name
            dic_line['work'] = dict(wk._fields['work_type'].selection).get(wk.work_type)
            dic_line['executor'] = wk.executor_id.name
            dic_line['opening_date'] = wk.opening_date
            dic_line['state'] = "Cerrada" if wk.state == 'closed' else "Abierta"
            dicc_emisor.setdefault(wk.emitter_id.name, []).append(dic_line)

        x = 2
        c = 0
        for value in dicc_emisor:
            y = x + len(dicc_emisor[value])-1
            c += len(dicc_emisor[value])
            if x == y:
                worksheet.write(x, 0, tools.ustr(value), normal_format)
            else:
                worksheet.merge_range(x, 0, y, 0, tools.ustr(value), normal_format)
            z = x

            for value1 in dicc_emisor[value]:
                worksheet.write(z, 1, value1['number'], normal_format)
                worksheet.write(z, 2, value1['code'], normal_format)
                worksheet.write(z, 3, value1['equipment'], normal_format)
                worksheet.write(z, 4, value1['work'], normal_format)
                worksheet.write(z, 5, value1['executor'], normal_format)
                worksheet.write(z, 6, value1['opening_date'], normal_format)
                worksheet.write(z, 7, value1['state'], normal_format)
                worksheet.write(z, 8, 1, normal_format)
                z += 1
            x = y+1
        worksheet.merge_range(x, 0, x, 7, tools.ustr("TOTAL GENERAL"), merge_format)
        worksheet.write(x, 8, c, merge_format)

OrdersPendingReport('report.turei_maintenance.orders_pending_report', 'wzd.orders.pending')
