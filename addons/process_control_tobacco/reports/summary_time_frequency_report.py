# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class SummaryTimeFrequencyToExcelTobaccoReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Resumen de Tiempo y Frecuencia'))
        if lines.turn:
            tecnolog_control = self.env['process_control_tobacco.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('turn', '=', lines.turn.id)])
        else:
            tecnolog_control = self.env['process_control_tobacco.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)])

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        normal_format1 = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        worksheet.merge_range('A1:E1', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA DESDE: %s - HASTA: %s") %(lines.date_start, lines.date_end), head_format)
        worksheet.set_column('A2:A2', 40)
        worksheet.set_column('B2:C2', 25)
        worksheet.write('A2', tools.ustr('Interrupción'), merge_format)
        worksheet.write('B2', tools.ustr('Tiempo(Horas)'), merge_format)
        worksheet.write('C2', tools.ustr('Frecuencia(U)'), merge_format)

        interruption, dic_interruption = self.env['process_control_tobacco.interruption.type'].search([]), {}

        for type in interruption:
            dic_interruption[type.name] = {'time': 0.0, 'frequency': 0}

        for tc in tecnolog_control:
            for it in tc.interruptions:
                if it.name in dic_interruption:
                    dic_interruption[it.name]['time'] = it.time + dic_interruption[it.name]['time']
                    dic_interruption[it.name]['frequency'] = it.frequency + dic_interruption[it.name][
                        'frequency']
                else:
                    dic_interruption[it.name] = {'time': 0.0, 'frequency': 0}
                    dic_interruption[it.name]['time'] = it.time + dic_interruption[it.name]['time']
                    dic_interruption[it.name]['frequency'] = it.frequency + dic_interruption[it.name][
                        'frequency']

        x = 2
        z = dic_interruption.items()
        z.sort(key=lambda x:(x[1]['time']), reverse=True)
        for l in z:
            if l[1]['time'] != 0.0:
                worksheet.write(x,0, l[0], normal_format)
                worksheet.write(x,1, round(l[1]['time']/60,2), normal_format)
                worksheet.write(x,2, l[1]['frequency'], normal_format)
                x += 1

SummaryTimeFrequencyToExcelTobaccoReport('report.process_control_tobacco.summary_time_frequency_report', 'wzd.summary.time.frequency.to.excel.tobacco')
