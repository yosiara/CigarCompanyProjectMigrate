# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class EfficiencyDphToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        list_endogenas, totaltend, totalfend = [], 0, 0
        list_exogenas, totaltexo, totalfexo = [], 0, 0
        total_turn, tab_p, heb_p, total_tabp, total_hebp, tte_tabp, tte_hebp, ttp_tabp, ttp_hebp, ttexo_tabp, ttexo_hebp, ttend_tabp, ttend_hebp = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        for li in self.env['process_control_primary.productive_line'].search([]):
            worksheet = workbook.add_worksheet(tools.ustr('Eficiencia %s') %(li.name))
            worksheet.merge_range('A1:F1', tools.ustr("Reporte de Eficiencia de la %s") %(li.name), head_format)
            worksheet.merge_range('A2:B2', tools.ustr("Desde"), merge_format)
            worksheet.merge_range('C2:D2', tools.ustr("Hasta"), merge_format)
            worksheet.merge_range('E2:F2', tools.ustr("Turno"), merge_format)
            worksheet.merge_range('A3:B3', tools.ustr(lines.date_start), normal_format)
            worksheet.merge_range('C3:D3', tools.ustr(lines.date_end), normal_format)
            worksheet.merge_range('E3:F3', tools.ustr(lines.turn.name[-1:] if lines.turn else "TODOS"), normal_format)
            worksheet.merge_range('A4:F4', tools.ustr("INTERRUPCIONES POR CAUSAS ENDÓGENAS (Internas)"), merge_format)
            worksheet.set_column('A5:A5', 25)
            worksheet.set_column('B5:F5', 15)
            worksheet.write('A5', tools.ustr('Interrupción'), merge_format)
            worksheet.write('B5', tools.ustr('Máquina'), merge_format)
            worksheet.write('C5', tools.ustr('Frecuencia'), merge_format)
            worksheet.write('D5', tools.ustr('Tiempo (min)'), merge_format)
            worksheet.write('E5', tools.ustr('% Frecuencia'), merge_format)
            worksheet.write('F5', tools.ustr('% Tiempo'), merge_format)
            if lines.turn:
                tecnolog_control = self.env['process_control_primary.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('productive_line','=',li.id),('turn', '=', lines.turn.id)])
            else:
                tecnolog_control = self.env['process_control_primary.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('productive_line','=',li.id)])
            if len(tecnolog_control) > 0:
                int_type, dic_endogenas, dic_exogenas, tfend, tfexo, ttend, ttexo, tp, ttp, tte = self.env['process_control_primary.interruption.type'].search([]), {}, {}, 0.0, 0.0, 0.0, 0.0, 0, 0, 0
                total_turn += len(tecnolog_control)
                for type in int_type:
                    if type.cause == 'exogena':
                        dic_exogenas[type.name] = {'time': 0, 'frequency': 0}

                for tc in tecnolog_control:
                    for it in tc.interruptions:
                        if it.interruption_type.cause == 'endogena':
                            valor = tools.ustr(it.interruption_type.name) + " " + tools.ustr(it.machine_type_id.name)
                            if valor in dic_endogenas:
                                dic_endogenas[valor]['time'] = it.time + dic_endogenas[valor]['time']
                                dic_endogenas[valor]['frequency'] = it.frequency + dic_endogenas[valor]['frequency']
                                dic_endogenas[valor]['machine'] = it.machine_type_id.name
                                tfend += it.frequency
                                ttend += it.time
                            else:
                                dic_endogenas[valor] = {'time': 0, 'frequency': 0, 'machine':''}
                                dic_endogenas[valor]['time'] = it.time + dic_endogenas[valor]['time']
                                dic_endogenas[valor]['frequency'] = it.frequency + dic_endogenas[valor]['frequency']
                                dic_endogenas[valor]['machine'] = it.machine_type_id.name
                                tfend += it.frequency
                                ttend += it.time
                        else:
                            dic_exogenas[it.interruption_type.name]['time'] = it.time + dic_exogenas[it.interruption_type.name]['time']
                            dic_exogenas[it.interruption_type.name]['frequency'] = it.frequency + dic_exogenas[it.interruption_type.name]['frequency']
                            tfexo += it.frequency
                            ttexo += it.time
                    tp += tc.production_in_production_system
                    ttp += tc.plan_time
                    tte += tc.execution_time
                totaltend += ttend
                totalfend += tfend
                totaltexo += ttexo
                totalfexo += tfexo
                x = 5
                z = dic_endogenas.items()
                z.sort(key=lambda x:(x[1]['time']), reverse=True)
                list_endogenas.append(z)
                for da in z:
                    if da[1]['time'] != 0.0:
                        worksheet.write(x,0, tools.ustr(da[0].replace(da[1]['machine'],'')), normal_format)
                        worksheet.write(x,1, tools.ustr(da[1]['machine']), normal_format)
                        worksheet.write(x,2, tools.ustr(da[1]['frequency']), normal_format)
                        worksheet.write(x,3, tools.ustr(da[1]['time']), normal_format)
                        worksheet.write(x,4, tools.ustr(round(da[1]['frequency'] * 100 / tfend, 2)), normal_format)
                        worksheet.write(x,5, tools.ustr(round(da[1]['time'] * 100 / ttend, 2)), normal_format)
                        x += 1
                worksheet.merge_range(x,0,x,1, tools.ustr("TOTAL DE INTERRUPCIONES"), merge_format)
                worksheet.write(x,2, tools.ustr(tfend), normal_format)
                worksheet.write(x,3, tools.ustr(ttend), normal_format)
                worksheet.write(x,4, tools.ustr(100), normal_format)
                worksheet.write(x,5, tools.ustr(100), normal_format)

                x += 1
                worksheet.merge_range(x,0,x,5, tools.ustr("INTERRUPCIONES POR CAUSAS EXÓGENAS (Externas)"), merge_format)
                x += 1
                worksheet.write(x,0, tools.ustr('Interrupción'), merge_format)
                worksheet.write(x,1, tools.ustr('Máquina'), merge_format)
                worksheet.write(x,2, tools.ustr('Frecuencia'), merge_format)
                worksheet.write(x,3, tools.ustr('Tiempo (min)'), merge_format)
                worksheet.write(x,4, tools.ustr('% Frecuencia'), merge_format)
                worksheet.write(x,5, tools.ustr('% Tiempo'), merge_format)

                x += 1
                z1 = dic_exogenas.items()
                z1.sort(key=lambda x:(x[1]['time']), reverse=True)
                list_exogenas.append(z1)
                for da in z1:
                    if da[1]['time'] != 0.0:
                        worksheet.write(x,0, tools.ustr(da[0]), normal_format)
                        worksheet.write(x,1, tools.ustr(''), normal_format)
                        worksheet.write(x,2, tools.ustr(da[1]['frequency']), normal_format)
                        worksheet.write(x,3, tools.ustr(da[1]['time']), normal_format)
                        worksheet.write(x,4, tools.ustr(round(da[1]['frequency'] * 100 / tfexo, 2)), normal_format)
                        worksheet.write(x,5, tools.ustr(round(da[1]['time'] * 100 / ttexo, 2)), normal_format)
                        x += 1
                worksheet.merge_range(x,0,x,1, tools.ustr("TOTAL DE INTERRUPCIONES"), merge_format)
                worksheet.write(x,2, tools.ustr(tfexo), normal_format)
                worksheet.write(x,3, tools.ustr(ttexo), normal_format)
                worksheet.write(x,4, tools.ustr(100), normal_format)
                worksheet.write(x,5, tools.ustr(100), normal_format)

                x += 1
                worksheet.merge_range(x,0,x,5, tools.ustr("TOTAL GENERAL"), merge_format)
                x += 1
                worksheet.write(x,0, tools.ustr("Turnos trabajados:"), merge_format)
                worksheet.write(x,1, tools.ustr(len(tecnolog_control)), normal_format)
                worksheet.merge_range(x,2,x,4, tools.ustr("Eficiencia real (%):"), merge_format)
                worksheet.write(x,5, tools.ustr(tp /(ttp * 3500)*100 if ttp != 0 else 0.0), normal_format)
                x += 1
                if li.codigo == 'LN':
                    cadena = "Tabaco Procesado"
                    tab_p = tp
                    total_tabp = len(tecnolog_control)
                    tte_tabp = tte
                    ttp_tabp = ttp
                    ttexo_tabp = ttexo
                    ttend_tabp = ttend
                else:
                    cadena = "Hebra Producida"
                    heb_p = tp
                    total_hebp = len(tecnolog_control)
                    tte_hebp = tte
                    ttp_hebp = ttp
                    ttexo_hebp = ttexo
                    ttend_hebp = ttend

                worksheet.write(x,0, tools.ustr(cadena + "(kg):"), merge_format)
                worksheet.write(x,1, tools.ustr(tp), normal_format)
                worksheet.merge_range(x,2,x,4, tools.ustr("Eficiencia operativa (%):"), merge_format)
                worksheet.write(x,5, tools.ustr(tp /((ttp-(ttexo/60)) * 3500)*100 if ((ttp-(ttexo/60)) * 3500) != 0 else 0.0), normal_format)
                x += 1
                worksheet.write(x,0, tools.ustr("Promedio de "+ cadena + " por turnos (kg):"), merge_format)
                worksheet.write(x,1, tools.ustr(tp/len(tecnolog_control)), normal_format)
                worksheet.merge_range(x,2,x,4, tools.ustr("Coeficiente de Disponibilidad Técnica (CDT):"), merge_format)
                worksheet.write(x,5, tools.ustr(round(((ttp-(ttend/60))/ttp)*100,2)), normal_format)
                x += 1
                worksheet.write(x,0, tools.ustr("Flujo de la "+ li.name + " (kg/h)"), merge_format)
                worksheet.write(x,1, tools.ustr(tp/tte if tte != 0 else 0.0), normal_format)
                worksheet.merge_range(x,2,x,4, tools.ustr(" "), merge_format)
                worksheet.write(x,5, tools.ustr(" "), normal_format)
                x += 1
                worksheet.merge_range(x,0,x,5, tools.ustr("ANÁLISIS DE UTILIZACIÓN DEL TIEMPO"), merge_format)
                x += 1
                worksheet.merge_range(x,0,x,1, tools.ustr(" "), merge_format)
                worksheet.merge_range(x,2,x,3, tools.ustr("Tiempo (horas)"), merge_format)
                worksheet.merge_range(x,4,x,5, tools.ustr("%"), merge_format)
                x += 1
                worksheet.merge_range(x,0,x,1, tools.ustr("Tiempo total planificado(horas):"), merge_format)
                worksheet.merge_range(x,2,x,3, tools.ustr(ttp), merge_format)
                worksheet.merge_range(x,4,x,5, tools.ustr(" "), merge_format)
                x += 1
                worksheet.merge_range(x,0,x,1, tools.ustr("Tiempo total de interrupciones(horas):"), merge_format)
                worksheet.merge_range(x,2,x,3, tools.ustr(round((ttend+ttexo)/60,2)), merge_format)
                worksheet.merge_range(x,4,x,5, tools.ustr(round(round((ttend+ttexo)/60,2)*100/ttp,2)), merge_format)
                x += 1
                worksheet.merge_range(x,0,x,1, tools.ustr("Tiempo real de producción(horas):"), merge_format)
                worksheet.merge_range(x,2,x,3, tools.ustr(round(tp/3500/60,2)), merge_format)
                worksheet.merge_range(x,4,x,5, tools.ustr(round(round(tp/3500/60,2)*100/ttp,2)), merge_format)
                x += 1
                worksheet.merge_range(x,0,x,1, tools.ustr("Tiempo no justificado(horas):"), merge_format)
                worksheet.merge_range(x,2,x,3, tools.ustr(round(ttp-((tp/3500/60)+((ttend+ttexo)/60)),2)), merge_format)
                worksheet.merge_range(x,4,x,5, tools.ustr(round(round(ttp-((tp/3500/60)+((ttend+ttexo)/60)),2)*100/ttp,2)), merge_format)


        worksheet1 = workbook.add_worksheet(tools.ustr('Eficiencia DPH'))
        worksheet1.merge_range('A1:F1', tools.ustr("Reporte de Eficiencia del Departamento de Producción de Hebra"), head_format)
        worksheet1.merge_range('A2:B2', tools.ustr("Desde"), merge_format)
        worksheet1.merge_range('C2:D2', tools.ustr("Hasta"), merge_format)
        worksheet1.merge_range('E2:F2', tools.ustr("Turno"), merge_format)
        worksheet1.merge_range('A3:B3', tools.ustr(lines.date_start), normal_format)
        worksheet1.merge_range('C3:D3', tools.ustr(lines.date_end), normal_format)
        worksheet1.merge_range('E3:F3', tools.ustr(lines.turn.name[-1:] if lines.turn else "TODOS"), normal_format)
        worksheet1.merge_range('A4:F4', tools.ustr("INTERRUPCIONES POR CAUSAS ENDÓGENAS (Internas)"), merge_format)
        worksheet1.set_column('A5:A5', 25)
        worksheet1.set_column('B5:F5', 15)
        worksheet1.write('A5', tools.ustr('Interrupción'), merge_format)
        worksheet1.write('B5', tools.ustr('Máquina'), merge_format)
        worksheet1.write('C5', tools.ustr('Frecuencia'), merge_format)
        worksheet1.write('D5', tools.ustr('Tiempo (min)'), merge_format)
        worksheet1.write('E5', tools.ustr('% Frecuencia'), merge_format)
        worksheet1.write('F5', tools.ustr('% Tiempo'), merge_format)
        x = 5
        for sub_le in list_endogenas:
            for le in sub_le:
                if le[1]['time'] != 0.0:
                    worksheet1.write(x,0, tools.ustr(le[0].replace(le[1]['machine'],'')), normal_format)
                    worksheet1.write(x,1, tools.ustr(le[1]['machine']), normal_format)
                    worksheet1.write(x,2, tools.ustr(le[1]['frequency']), normal_format)
                    worksheet1.write(x,3, tools.ustr(le[1]['time']), normal_format)
                    worksheet1.write(x,4, tools.ustr(round(le[1]['frequency'] * 100 / totalfend, 2)), normal_format)
                    worksheet1.write(x,5, tools.ustr(round(le[1]['time'] * 100 / totaltend, 2)), normal_format)
                    x += 1

        worksheet1.merge_range(x,0,x,1, tools.ustr("TOTAL DE INTERRUPCIONES"), merge_format)
        worksheet1.write(x,2, tools.ustr(totalfend), normal_format)
        worksheet1.write(x,3, tools.ustr(totaltend), normal_format)
        worksheet1.write(x,4, tools.ustr(100), normal_format)
        worksheet1.write(x,5, tools.ustr(100), normal_format)

        x += 1
        worksheet1.merge_range(x,0,x,5, tools.ustr("INTERRUPCIONES POR CAUSAS EXÓGENAS (Externas)"), merge_format)
        x += 1
        worksheet1.write(x,0, tools.ustr('Interrupción'), merge_format)
        worksheet1.write(x,1, tools.ustr('Máquina'), merge_format)
        worksheet1.write(x,2, tools.ustr('Frecuencia'), merge_format)
        worksheet1.write(x,3, tools.ustr('Tiempo (min)'), merge_format)
        worksheet1.write(x,4, tools.ustr('% Frecuencia'), merge_format)
        worksheet1.write(x,5, tools.ustr('% Tiempo'), merge_format)

        x += 1
        for sub_le in list_exogenas:
            for le in sub_le:
                if le[1]['time'] != 0.0:
                    worksheet1.write(x,0, tools.ustr(le[0]), normal_format)
                    worksheet1.write(x,1, tools.ustr(" "), normal_format)
                    worksheet1.write(x,2, tools.ustr(le[1]['frequency']), normal_format)
                    worksheet1.write(x,3, tools.ustr(le[1]['time']), normal_format)
                    worksheet1.write(x,4, tools.ustr(round(le[1]['frequency'] * 100 / totalfexo, 2)), normal_format)
                    worksheet1.write(x,5, tools.ustr(round(le[1]['time'] * 100 / totaltexo, 2)), normal_format)
                    x += 1

        worksheet1.merge_range(x,0,x,1, tools.ustr("TOTAL DE INTERRUPCIONES"), merge_format)
        worksheet1.write(x,2, tools.ustr(totalfexo), normal_format)
        worksheet1.write(x,3, tools.ustr(totaltexo), normal_format)
        worksheet1.write(x,4, tools.ustr(100), normal_format)
        worksheet1.write(x,5, tools.ustr(100), normal_format)

        x += 1
        worksheet1.merge_range(x,0,x,5, tools.ustr("TOTAL GENERAL"), merge_format)
        x += 1
        worksheet1.write(x,0, tools.ustr("Turnos trabajados:"), merge_format)
        worksheet1.write(x,1, tools.ustr(total_turn), normal_format)
        worksheet1.merge_range(x,2,x,5, tools.ustr(" "), merge_format)
        x += 1
        worksheet1.write(x,0, tools.ustr("Tabaco Procesado(kg):"), merge_format)
        worksheet1.write(x,1, tools.ustr(tab_p), normal_format)
        worksheet1.merge_range(x,2,x,4, tools.ustr("Hebra Producida(kg):"), merge_format)
        worksheet1.write(x,5, tools.ustr(heb_p), normal_format)
        x += 1
        worksheet1.write(x,0, tools.ustr("Promedio de tabaco procesado por turnos:"), merge_format)
        worksheet1.write(x,1, tools.ustr(tab_p/total_tabp if total_tabp !=0 else 0), normal_format)
        worksheet1.merge_range(x,2,x,4, tools.ustr("Promedio de hebra producida por turnos:"), merge_format)
        worksheet1.write(x,5, tools.ustr(heb_p/total_hebp if total_hebp != 0 else 0), normal_format)
        x += 1
        worksheet1.write(x,0, tools.ustr("Flujo de la Línea Normal (kg/h)"), merge_format)
        worksheet1.write(x,1, tools.ustr(tab_p/tte_tabp if tte_tabp != 0 else 0.0), normal_format)
        worksheet1.merge_range(x,2,x,4, tools.ustr("Flujo de la Línea de Corte y Secado (kg/h)"), merge_format)
        worksheet1.write(x,5, tools.ustr(heb_p/tte_hebp if tte_hebp != 0 else 0.0), normal_format)
        x += 1
        worksheet1.write(x,0, tools.ustr("Eficiencia real LN (%):"), merge_format)
        worksheet1.write(x,1, tools.ustr(tab_p /(ttp_tabp * 3500)*100 if ttexo_tabp != 0 else 0), normal_format)
        worksheet1.merge_range(x,2,x,4, tools.ustr("Eficiencia real LCS(%):"), merge_format)
        worksheet1.write(x,5, tools.ustr(heb_p /(ttp_hebp * 3500)*100 if ttp_hebp != 0 else 0), normal_format)
        x += 1
        worksheet1.write(x,0, tools.ustr("Eficiencia operativa LN(%):"), merge_format)
        worksheet1.write(x,1, tools.ustr(tab_p /((ttp_tabp-(ttexo_tabp/60)) * 3500)*100 if ((ttp_tabp-(ttexo_tabp/60)) * 3500) !=0 else 0), normal_format)
        worksheet1.merge_range(x,2,x,4, tools.ustr("Eficiencia operativa LCS (%):"), merge_format)
        worksheet1.write(x,5, tools.ustr(heb_p /((ttp_hebp-(ttexo_hebp/60)) * 3500)*100 if (ttp_hebp-(ttexo_hebp/60)) != 0 else 0), normal_format)
        x += 1
        worksheet1.write(x,0, tools.ustr("Coeficiente de Disponibilidad Técnica LN(CDT):"), merge_format)
        worksheet1.write(x,1, tools.ustr(round(((ttp_tabp-(ttend_tabp/60))/ttp_tabp)*100,2) if ttp_tabp !=0 else 0), normal_format)
        worksheet1.merge_range(x,2,x,4, tools.ustr("Coeficiente de Disponibilidad Técnica LCS(CDT):"), merge_format)
        worksheet1.write(x,5, tools.ustr(round(((ttp_hebp-(ttend_hebp/60))/ttp_hebp)*100 if ttp_hebp != 0 else 0,2)), normal_format)
        x += 1
        worksheet1.merge_range(x,0,x,3, tools.ustr("Eficiencia real DPH(%):"), merge_format)
        worksheet1.merge_range(x,4,x,5, tools.ustr(0), normal_format)
        x += 1
        worksheet1.merge_range(x,0,x,3, tools.ustr("Eficiencia operativa DPH (%):"), merge_format)
        worksheet1.merge_range(x,4,x,5, tools.ustr(0), normal_format)
        x += 1
        worksheet1.merge_range(x,0,x,3, tools.ustr("Coeficiente de Disponibilidad Técnica DPH (CDT):"), merge_format)
        worksheet1.merge_range(x,4,x,5, tools.ustr(0), normal_format)
        x += 1
        worksheet1.merge_range(x,0,x,5, tools.ustr("ANÁLISIS DE UTILIZACIÓN DEL TIEMPO"), merge_format)
        x += 1
        worksheet1.merge_range(x,0,x,1, tools.ustr(" "), merge_format)
        worksheet1.merge_range(x,2,x,3, tools.ustr("Tiempo (horas)"), merge_format)
        worksheet1.merge_range(x,4,x,5, tools.ustr("%"), merge_format)
        x += 1
        worksheet1.merge_range(x,0,x,1, tools.ustr("Tiempo total planificado(horas):"), merge_format)
        worksheet1.merge_range(x,2,x,3, tools.ustr((ttp_tabp + ttp_hebp)/2), merge_format)
        worksheet1.merge_range(x,4,x,5, tools.ustr(" "), merge_format)
        x += 1
        worksheet1.merge_range(x,0,x,1, tools.ustr("Tiempo total de interrupciones(horas):"), merge_format)
        worksheet1.merge_range(x,2,x,3, tools.ustr(round((ttend_tabp+ttend_hebp+ttexo_tabp+ttexo_hebp)/60,2)), merge_format)
        worksheet1.merge_range(x,4,x,5, tools.ustr(round(round((ttend_tabp+ttend_hebp+ttexo_tabp+ttexo_hebp)/60,2)*100/((ttp_tabp + ttp_hebp)/2) if ((ttp_tabp + ttp_hebp)/2) !=0 else 0,2)), merge_format)
        x += 1
        worksheet1.merge_range(x,0,x,1, tools.ustr("Tiempo real de producción(horas):"), merge_format)
        worksheet1.merge_range(x,2,x,3, tools.ustr(0), merge_format)
        worksheet1.merge_range(x,4,x,5, tools.ustr(0), merge_format)
        x += 1
        worksheet1.merge_range(x,0,x,1, tools.ustr("Tiempo no justificado(horas):"), merge_format)
        worksheet1.merge_range(x,2,x,3, tools.ustr(0), merge_format)
        worksheet1.merge_range(x,4,x,5, tools.ustr(0), merge_format)

EfficiencyDphToExcelReport('report.process_control_primary.efficiency_dph_report', 'wzd.efficiency.dph.to.excel')
