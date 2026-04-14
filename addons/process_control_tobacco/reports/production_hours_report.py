# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ProductionHoursToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        production_hours = self.env['process_control_tobacco.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)], order="date")

        worksheet = workbook.add_worksheet(tools.ustr("Seccion Mañana"))
        worksheet1 = workbook.add_worksheet(tools.ustr("Seccion Tarde"))

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Año'), merge_format)
        worksheet.write('B4', 'Mes', merge_format)
        worksheet.write('C4', 'Dia', merge_format)
        worksheet.set_column('D4:D4', 20)
        worksheet.write('D4', 'Turno', merge_format)
        worksheet.set_row(3,45)
        worksheet.set_column('C4:J4', 10)
        worksheet.write('E4', '1era Hora 7 a.m - 8 a.m', merge_format)
        worksheet.write('F4', '2da Hora 8 a.m - 9 a.m', merge_format)
        worksheet.write('G4', '3ra Hora 9 a.m - 10 a.m', merge_format)
        worksheet.write('H4', '4ta Hora 10 a.m - 11 a.m', merge_format)
        worksheet.write('I4', '5ta Hora 11 a.m - 12 p.m', merge_format)
        worksheet.write('J4', '6ta Hora 12 p.m - 1 p.m', merge_format)
        worksheet.write('K4', '7ma Hora 1 p.m - 2 p.m', merge_format)
        worksheet.write('L4', '8va Hora 2 p.m - 3 p.m', merge_format)

        worksheet1.write('A4', tools.ustr('Año'), merge_format)
        worksheet1.write('B4', 'Mes', merge_format)
        worksheet1.write('C4', 'Dia', merge_format)
        worksheet1.set_column('D4:D4', 20)
        worksheet1.write('D4', 'Turno', merge_format)
        worksheet1.set_row(3,45)
        worksheet1.set_column('C4:J4', 10)
        worksheet1.write('E4', '1era Hora 3 p.m - 4 p.m', merge_format)
        worksheet1.write('F4', '2da Hora 4 p.m - 5 p.m', merge_format)
        worksheet1.write('G4', '3ra Hora 5 p.m - 6 p.m', merge_format)
        worksheet1.write('H4', '4ta Hora 6 p.m - 7 p.m', merge_format)
        worksheet1.write('I4', '5ta Hora 7 p.m - 8 p.m', merge_format)
        worksheet1.write('J4', '6ta Hora 8 p.m - 9 p.m', merge_format)
        worksheet1.write('K4', '7ma Hora 9 p.m - 10 p.m', merge_format)
        worksheet1.write('L4', '8va Hora 10 p.m - 11 p.m', merge_format)

        x = 4
        z = 4
        for ph in production_hours:
            if ph.attendance_id.name == tools.ustr('Mañana'):
                worksheet.write(x, 0, ph.date.split('-')[0], normal_format)
                worksheet.write(x, 1, ph.date.split('-')[1], normal_format)
                worksheet.write(x, 2, ph.date.split('-')[2], normal_format)
                worksheet.write(x, 3, ph.turn.turn.name[-1:], normal_format)

                y = 4
                for h in ph.production_by_hours_ids:
                    worksheet.write(x, y, h.production_count, normal_format)
                    y += 1
                x += 1
            if ph.attendance_id.name == tools.ustr('Tarde'):
                worksheet1.write(z, 0, ph.date.split('-')[0], normal_format)
                worksheet1.write(z, 1, ph.date.split('-')[1], normal_format)
                worksheet1.write(z, 2, ph.date.split('-')[2], normal_format)
                worksheet1.write(z, 3, ph.turn.turn.name[-1:], normal_format)

                g = 4
                for h in ph.production_by_hours_ids:
                    worksheet1.write(z, g, h.production_count, normal_format)
                    g += 1
                z += 1


ProductionHoursToExcelReport('report.process_control_tobacco.production_hours_report', 'wzd.production.hours.to.excel')
