# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class SummaryTimeFrequencyToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Resumen de Tiempo y Frecuencia'))
        if lines.turn:
            tecnolog_control = self.env['process_control_primary.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('turn', '=', lines.turn.id)])
        else:
            tecnolog_control = self.env['process_control_primary.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)])

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        normal_format1 = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        worksheet.merge_range('A1:E1', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA DESDE: %s - HASTA: %s") %(lines.date_start, lines.date_end), head_format)
        worksheet.set_column('A2:A2', 40)
        worksheet.set_column('B2:B2', 25)
        worksheet.set_column('E2:E2', 20)
        worksheet.write('A2', tools.ustr('Interrupción'), merge_format)
        worksheet.write('B2', tools.ustr('Línea'), merge_format)
        worksheet.write('C2', tools.ustr('UM'), merge_format)
        worksheet.write('D2', tools.ustr('Tiempo'), merge_format)
        worksheet.write('E2', tools.ustr('Frecuencia'), merge_format)


        interruption, dic_interruption_ln, dic_interruption_lcs = self.env['process_control_primary.interruption.type'].search([]), {}, {}
        for type in interruption:
            dic_interruption_ln[type.name] = {'time': 0.0, 'frequency': 0, 'linea':''}
            dic_interruption_lcs[type.name] = {'time': 0.0, 'frequency': 0, 'linea':''}

        for tc in tecnolog_control:
            for it in tc.interruptions:
                if tc. productive_line.name == 'Línea Corte y Secado':
                    if it.name in dic_interruption_lcs:
                        dic_interruption_lcs[it.name]['time'] = it.time + dic_interruption_lcs[it.name]['time']
                        dic_interruption_lcs[it.name]['frequency'] = it.frequency + dic_interruption_lcs[it.name]['frequency']
                        dic_interruption_lcs[it.name]['linea'] = tc. productive_line.name
                    else:
                        dic_interruption_lcs[it.name] = {'time': 0.0, 'frequency': 0, 'linea':''}
                        dic_interruption_lcs[it.name]['time'] = it.time + dic_interruption_lcs[it.name]['time']
                        dic_interruption_lcs[it.name]['frequency'] = it.frequency + dic_interruption_lcs[it.name]['frequency']
                        dic_interruption_lcs[it.name]['linea'] = tc. productive_line.name

                else:
                    if it.name in dic_interruption_ln:
                        dic_interruption_ln[it.name]['time'] = it.time + dic_interruption_ln[it.name]['time']
                        dic_interruption_ln[it.name]['frequency'] = it.frequency + dic_interruption_ln[it.name]['frequency']
                        dic_interruption_ln[it.name]['linea'] = tc. productive_line.name
                    else:
                        dic_interruption_ln[it.name] = {'time': 0.0, 'frequency': 0, 'linea':''}
                        dic_interruption_ln[it.name]['time'] = it.time + dic_interruption_ln[it.name]['time']
                        dic_interruption_ln[it.name]['frequency'] = it.frequency + dic_interruption_ln[it.name]['frequency']
                        dic_interruption_ln[it.name]['linea'] = tc. productive_line.name

        x = 2
        z = dic_interruption_lcs.items()
        z.sort(key=lambda x:(x[1]['time']), reverse=True)
        for lcs in z:
            if lcs[1]['time'] != 0.0:
                worksheet.write(x,0, tools.ustr(lcs[0]), normal_format)
                worksheet.write(x,1, tools.ustr(lcs[1]['linea']), normal_format)
                worksheet.write(x,2, tools.ustr("Hora"), normal_format)
                worksheet.write(x,3, tools.ustr(round(lcs[1]['time']/60,2)), normal_format)
                worksheet.write(x,4, tools.ustr(lcs[1]['frequency']), normal_format)
                x += 1

        z1 = dic_interruption_ln.items()
        z1.sort(key=lambda x:(x[1]['time']), reverse=True)
        for ln in z1:
            if ln[1]['time'] != 0.0:
                worksheet.write(x,0, tools.ustr(ln[0]), normal_format)
                worksheet.write(x,1, tools.ustr(ln[1]['linea']), normal_format)
                worksheet.write(x,2, tools.ustr("Hora"), normal_format)
                worksheet.write(x,3, tools.ustr(round(ln[1]['time']/60,2)), normal_format)
                worksheet.write(x,4, tools.ustr(ln[1]['frequency']), normal_format)
                x += 1

SummaryTimeFrequencyToExcelReport('report.process_control_primary.summary_time_frequency_report', 'wzd.summary.time.frequency.to.excel')
