# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class UseOfTimeToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Utilización del Tiempo'))
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        tecnolog_control = self.env['process_control_primary.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)], order='date')
        worksheet.merge_range('A1:J1', tools.ustr("REPORTE DE UTILIZACIÓN DEL TIEMPO DESDE: %s - HASTA: %s") %(lines.date_start, lines.date_end), head_format)
        worksheet.set_column('A2:D2', 7)
        worksheet.write('A2', tools.ustr('Año'), merge_format)
        worksheet.write('B2', 'Mes', merge_format)
        worksheet.write('C2', tools.ustr('Día'), merge_format)
        worksheet.write('D2', tools.ustr('Turno'), merge_format)
        worksheet.set_column('E2:J2', 25)
        worksheet.write('E2', tools.ustr('Tiempo Total Planificado'), merge_format)
        worksheet.write('F2', tools.ustr('Tiempo Real Trabajado'), merge_format)
        worksheet.write('G2', tools.ustr('Tiempo Total de Interrupciones'), merge_format)
        worksheet.write('H2', tools.ustr('Tiempo no Justificado'), merge_format)
        worksheet.write('I2', tools.ustr('Tiempo Perdido por Causas Exógenas'), merge_format)
        worksheet.write('J2', tools.ustr('Tiempo Perdido por Causas Endógenas'), merge_format)

        x = 2
        print len(tecnolog_control)
        for tc in tecnolog_control:
            tti, tpexo, tpend = 0.0, 0.0, 0.0
            worksheet.write(x, 0, tc.date.split('-')[0], normal_format)
            worksheet.write(x, 1, tc.date.split('-')[1], normal_format)
            worksheet.write(x, 2, tc.date.split('-')[2], normal_format)
            worksheet.write(x, 3, tc.turn.name[-1:], normal_format)
            worksheet.write(x, 4, tc.plan_time, normal_format)

            worksheet.write(x, 5, round(tc.production_in_production_system/tc.productive_capacity,2), normal_format)

            for it in tc.interruptions:
                tti += it.time
                if it.interruption_type.cause == 'exogena':
                    tpexo += it.time
                if it.interruption_type.cause == 'endogena':
                    tpend += it.time

            worksheet.write(x, 6, round(tti/60,2), normal_format)
            tnj = tc.plan_time-(round(tc.production_in_production_system/tc.productive_capacity,2) + round(tti/60,2))
            worksheet.write(x, 7, tnj, normal_format)
            worksheet.write(x, 8, round(tpexo/60,2), normal_format)
            worksheet.write(x, 9, round(tpend/60,2), normal_format)
            x += 1


UseOfTimeToExcelReport('report.process_control_primary.use_of_time_report', 'wzd.use.of.time.to.excel')
