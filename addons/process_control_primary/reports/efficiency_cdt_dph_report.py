# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class EfficiencyCdtDphToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        worksheet = workbook.add_worksheet(tools.ustr('Eficiencia y CDT del DPH'))
        tecnolog_control = self.env['process_control_primary.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)], order='date, turn')
        worksheet.merge_range('A1:G1', tools.ustr("REPORTE DE EFICIENCIA Y CDT DPH DESDE: %s - HASTA: %s") %(lines.date_start, lines.date_end), merge_format)
        worksheet.set_column('A2:D2', 7)
        worksheet.write('A2', tools.ustr('Año'), merge_format)
        worksheet.write('B2', 'Mes', merge_format)
        worksheet.write('C2', tools.ustr('Día'), merge_format)
        worksheet.write('D2', tools.ustr('Turno'), merge_format)
        worksheet.set_column('E2:G2', 25)
        worksheet.write('E2', tools.ustr('Eficiencia Real'), merge_format)
        worksheet.write('F2', tools.ustr('Eficiencia Operativa'), merge_format)
        worksheet.write('G2', tools.ustr('Coeficiente de Disponibilidad Técnica Real'), merge_format)
        x = 2
        for tc in tecnolog_control:
            tpexo, tpend = 0.0, 0.0
            worksheet.write(x, 0, tc.date.split('-')[0], normal_format)
            worksheet.write(x, 1, tc.date.split('-')[1], normal_format)
            worksheet.write(x, 2, tc.date.split('-')[2], normal_format)
            worksheet.write(x, 3, tc.turn.name[-1:], normal_format)
            efficiency_real = (tc.production_in_production_system / (tc.plan_time * tc.productive_capacity)) * 100
            worksheet.write(x, 4, round(efficiency_real,2), normal_format)
            for it in tc.interruptions:
                if it.interruption_type.cause == 'exogena':
                    tpexo += it.time
                if it.interruption_type.cause == 'endogena':
                    tpend += it.time
            efficiency_operative = (tc.production_in_production_system / ((tc.plan_time -(tpexo / 60)) * tc.productive_capacity)) * 100
            worksheet.write(x, 5, round(efficiency_operative,2), normal_format)
            cdt = ((tc.plan_time-(tpend / 60))/tc.plan_time) * 100
            worksheet.write(x, 6, round(cdt,2), normal_format)
            x += 1



EfficiencyCdtDphToExcelReport('report.process_control_primary.efficiency_cdt_dph_report', 'wzd.efficiency.cdt.dph.to.excel')
