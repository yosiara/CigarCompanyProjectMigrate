# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class InterruptionToExcelTobaccoReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Interrupciones'))
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        tecnolog_control = self.env['process_control_tobacco.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)], order='date')
        worksheet.merge_range('A1:I1', tools.ustr("REPORTE DE INTERRUPCIONES DESDE: %s - HASTA: %s") %(lines.date_start, lines.date_end), head_format)
        worksheet.set_column('A2:D2', 7)
        worksheet.write('A2', tools.ustr('Año'), merge_format)
        worksheet.write('B2', 'Mes', merge_format)
        worksheet.write('C2', tools.ustr('Día'), merge_format)
        worksheet.write('D2', tools.ustr('Turno'), merge_format)
        worksheet.set_column('E2:E2', 25)
        worksheet.write('E2', tools.ustr('Línea'), merge_format)
        worksheet.set_column('F2:F2', 15)
        worksheet.write('F2', tools.ustr('Máquina'), merge_format)
        worksheet.set_column('G2:G2', 30)
        worksheet.write('G2', tools.ustr('Tipo de interrupción'), merge_format)
        worksheet.set_column('H2:I2', 12)
        worksheet.write('H2', tools.ustr('Tiempo (minutos)'), merge_format)
        worksheet.write('I2', tools.ustr('Frecuencia'), merge_format)

        x = 2
        for tc in tecnolog_control:
            for it in tc.interruptions:
                worksheet.write(x, 0, tc.date.split('-')[0], normal_format)
                worksheet.write(x, 1, tc.date.split('-')[1], normal_format)
                worksheet.write(x, 2, tc.date.split('-')[2], normal_format)
                worksheet.write(x, 3, tc.turn.turn.name[-1:], normal_format)
                worksheet.write(x, 4, tools.ustr("LTR"), normal_format)
                worksheet.write(x, 5, tools.ustr(it.machine_type_id.name or ''), normal_format)
                worksheet.write(x, 6, tools.ustr(it.interruption_type.name), normal_format)
                worksheet.write(x, 7, it.time, normal_format)
                worksheet.write(x, 8, it.frequency, normal_format)
                x += 1

InterruptionToExcelTobaccoReport('report.process_control_tobacco.interruption_report', 'wzd.interruption.to.excel.tobacco')
