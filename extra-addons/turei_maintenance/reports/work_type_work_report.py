# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class WorkTypeWorkReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})

        work_type = ['imp-tec', 'imp_ope', 'plan_ciclo', 'plan_et', 'ins_tec']

        for mt in work_type:
            work_order = self.env['turei_maintenance.work_order'].search([('opening_date', '>=', lines.date_start), ('opening_date', '<=', lines.date_end), ('work_type', '=', mt)])
            worksheet = workbook.add_worksheet(tools.ustr(mt))
            worksheet.write(0, 0, tools.ustr("Código"), merge_format)
            worksheet.set_column('B0:D0', 15)
            worksheet.write(0, 1, tools.ustr("Número"), merge_format)
            worksheet.write(0, 2, tools.ustr("Fecha Apertura"), merge_format)
            worksheet.write(0, 3, tools.ustr("Fecha Cierre"), merge_format)
            worksheet.set_column('E0:E0', 45)
            worksheet.write(0, 4, tools.ustr("Equipo"), merge_format)
            worksheet.set_column('F0:F0', 30)
            worksheet.write(0, 5, tools.ustr("Taller"), merge_format)
            worksheet.set_column('G0:G0', 20)
            worksheet.write(0, 6, tools.ustr("Línea"), merge_format)
            worksheet.write(0, 7, tools.ustr("Estado"), merge_format)
            x = 1
            for wk in work_order:
                worksheet.write(x, 0, wk.code, normal_format)
                worksheet.write(x, 1, wk.number_new, normal_format)
                worksheet.write(x, 2, wk.opening_date, normal_format)
                worksheet.write(x, 3, wk.closing_date, normal_format)
                worksheet.write(x, 4, wk.equipament_id.name, normal_format)
                worksheet.write(x, 5, wk.category_id.name, normal_format)
                worksheet.write(x, 6, wk.line_id.name, normal_format)
                worksheet.write(x, 7, dict(wk._fields['state'].selection).get(wk.state), normal_format)
                x += 1

WorkTypeWorkReport('report.turei_maintenance.work_type_work_report', 'wzd.work.type.work')
