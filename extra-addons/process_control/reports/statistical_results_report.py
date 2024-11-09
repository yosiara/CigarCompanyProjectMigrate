# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class StatisticalResultsToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        productive_sections = self.env['turei_process_control.productive_section'].search([('active', '=', True)], order="name")
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        normal_format1 = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        p_cajones_turn, r_caje_turn, ind_rech_turn, acum_ind_rech_turn, cdt_turn, tnj_turn_p_acum = 0.0, 0, 0.0, 0.0, 0.0, 0.0
        p_cajones_turn_acum, r_caje_turn_acum, ttp_turn, trp_turn, ttig_turn, tnj_turn, tt_turn_acum = 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0
        ttp_turn_p, trp_turn_p, ttig_turn_p, tnj_turn_p, tt_turn, prc_turn, er_turn, eo_turn = 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0
        ttp_turn_acum, trp_turn_acum, ttig_turn_acum, tnj_turn_acum, trp_turn_p_acum, ttig_turn_p_acum = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        prc_acum, er_turn_acum, eo_turn_acum, cdt_turn_acum, cturnmt, cturntt, cturnmt1, cturntt1 = 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0
        day_values_turn2, day_values_turn1, tf_turn, tf_turn_acum, acum_values_turn, acum1_values_turn, acum_values_turn1, acum1_values_turn1 = {}, {}, 0, 0, {}, {}, {}, {}
        for gi in self.env['turei_process_control.interruption.type'].search([]):
            day_values_turn1[gi.code] = {'time': 0.0, 'frequency': 0.0}
            day_values_turn2[gi.code] = {'time': 0.0, 'frequency': 0.0}
        for i in xrange(1,9):
            acum_values_turn[i] = 0.0
            acum1_values_turn[i] = 0.0
            acum_values_turn1[i] = 0.0
            acum1_values_turn1[i] = 0.0

        for ps in productive_sections:
            worksheet = workbook.add_worksheet(tools.ustr('Sp.' + ps.name[-2:]))
            worksheet.merge_range('A1:S1', tools.ustr("RESULTADOS ESTADÍSTICOS DE CONTROL DEL PROCESO"), head_format)
            worksheet.merge_range('A2:D2', tools.ustr('Seccion Productiva: ' + ps.name[-2:]), head_format)
            worksheet.merge_range('F2:J2', tools.ustr('Turno: %s') %(lines.turn.name[-1:]), head_format)
            worksheet.merge_range('O2:S2', tools.ustr('Fecha: %s') %(lines.date_start), head_format)

            worksheet.merge_range('A3:E3', tools.ustr('Indicadores'), merge_format)
            worksheet.merge_range('F3:H3', tools.ustr('Día'), merge_format)
            worksheet.merge_range('I3:K3', tools.ustr('Acumulado'), merge_format)
            worksheet.merge_range('A4:E4', tools.ustr('Análisis de utilización del tiempo '), merge_format)
            worksheet.merge_range('F4:G4', tools.ustr('Tiempo (hr)'), merge_format)
            worksheet.write('H4', tools.ustr('%'), merge_format)
            worksheet.merge_range('I4:J4', tools.ustr('Tiempo (hr)'), merge_format)
            worksheet.write('K4', tools.ustr('%'), merge_format)
            worksheet.merge_range('A5:E5', tools.ustr('Tiempo total planificado'), normal_format)
            worksheet.merge_range('A6:E6', tools.ustr('Tiempo real de producción'), normal_format)
            worksheet.merge_range('A7:E7', tools.ustr('Tiempo total de interrupciones generales'), normal_format)
            worksheet.merge_range('A8:E8', tools.ustr('Tiempo no justificado'), normal_format)

            worksheet.merge_range('M3:Q3', tools.ustr('Indicadores'), merge_format)
            worksheet.write('R3', tools.ustr('Día'), merge_format)
            worksheet.write('S3', tools.ustr('Acum'), merge_format)
            worksheet.merge_range('M4:Q4', tools.ustr('Turnos trabajados'), normal_format)
            worksheet.merge_range('M5:Q5', tools.ustr('Producción realizada (cajones)'), normal_format)
            worksheet.merge_range('M6:Q6', tools.ustr('Promedio de cajones/ turno'), normal_format)
            worksheet.merge_range('M7:Q7', tools.ustr('Eficiencia real (%)'), normal_format)
            worksheet.merge_range('M8:Q8', tools.ustr('Eficiencia operativa (%)'), normal_format)
            worksheet.merge_range('M9:Q9', tools.ustr('CDT Real (%)'), normal_format)
            worksheet.merge_range('M10:Q10', tools.ustr('CDT Operativo (%)'), normal_format)

            worksheet.merge_range('A11:S11', tools.ustr('Día'), merge_format)
            worksheet.set_column('A12:A12', 15)

            worksheet.write('A12', tools.ustr('Interrupciones'), normal_format)
            worksheet.write('A13', tools.ustr('Tiempo (hr)'), normal_format)
            worksheet.write('A14', tools.ustr('Frecuencia'), normal_format)
            worksheet.write('A15', tools.ustr('% Tiempo'), normal_format)
            worksheet.write('A16', tools.ustr('% Frecuencia'), normal_format)

            worksheet.merge_range('A17:S17', tools.ustr('Acumulado'), merge_format)

            worksheet.write('A18', tools.ustr('Interrupciones'), normal_format)
            worksheet.write('A19', tools.ustr('Tiempo (hr)'), normal_format)
            worksheet.write('A20', tools.ustr('Frecuencia'), normal_format)
            worksheet.write('A21', tools.ustr('% Tiempo'), normal_format)
            worksheet.write('A22', tools.ustr('% Frecuencia'), normal_format)

            worksheet.merge_range('A23:S23', tools.ustr('Producción y Rechazo de las AMF'), merge_format)
            worksheet.merge_range('D24:G24', tools.ustr('Día'), merge_format)
            worksheet.merge_range('H24:I24', tools.ustr('Brigada'), merge_format)
            worksheet.merge_range('D25:G25', tools.ustr('Indicadores'), normal_format)
            worksheet.merge_range('D26:G26', tools.ustr('Producción (cajones)'), normal_format)
            worksheet.merge_range('D27:G27', tools.ustr('Rechazo (cajones)'), normal_format)
            worksheet.merge_range('D28:G28', tools.ustr('Índice de Rechazo Ln (%)'), normal_format)
            worksheet.merge_range('D29:G29', tools.ustr('Índice de Rechazo B (%)'), normal_format)

            worksheet.merge_range('K24:N24', tools.ustr('Acumulado'), merge_format)
            worksheet.merge_range('O24:P24', tools.ustr('Brigada'), merge_format)
            worksheet.merge_range('K25:N25', tools.ustr('Indicadores'), normal_format)
            worksheet.merge_range('K26:N26', tools.ustr('Producción (cajones)'), normal_format)
            worksheet.merge_range('K27:N27', tools.ustr('Rechazo (cajones)'), normal_format)
            worksheet.merge_range('K28:N28', tools.ustr('Índice de Rechazo Ln (%)'), normal_format)
            worksheet.merge_range('K29:N29', tools.ustr('Índice de Rechazo B (%)'), normal_format)

            worksheet.merge_range('A30:A31', tools.ustr('Indicadores'), merge_format)
            worksheet.write('A32', tools.ustr('Día'), normal_format)
            worksheet.write('A33', tools.ustr('Acumulado'), normal_format)
            worksheet.write('B30', tools.ustr('1era'), normal_format1)
            worksheet.write('B31', tools.ustr('7-8'), normal_format1)
            worksheet.write('C30', tools.ustr('2da'), normal_format1)
            worksheet.write('C31', tools.ustr('8-9'), normal_format1)
            worksheet.write('D30', tools.ustr('3era'), normal_format1)
            worksheet.write('D31', tools.ustr('9-10'), normal_format1)
            worksheet.write('E30', tools.ustr('4ta'), normal_format1)
            worksheet.write('E31', tools.ustr('10-11'), normal_format1)
            worksheet.write('F30', tools.ustr('5ta'), normal_format1)
            worksheet.write('F31', tools.ustr('11-12'), normal_format1)
            worksheet.write('G30', tools.ustr('6ta'), normal_format1)
            worksheet.write('G31', tools.ustr('12-1'), normal_format1)
            worksheet.write('H30', tools.ustr('7ma'), normal_format1)
            worksheet.write('H31', tools.ustr('1-2'), normal_format1)
            worksheet.write('I30', tools.ustr('8va'), normal_format1)
            worksheet.write('I31', tools.ustr('2-3'), normal_format1)

            worksheet.write('J30', tools.ustr('1era'), normal_format1)
            worksheet.write('J31', tools.ustr('3-4'), normal_format1)
            worksheet.write('K30', tools.ustr('2da'), normal_format1)
            worksheet.write('K31', tools.ustr('4-5'), normal_format1)
            worksheet.write('L30', tools.ustr('3era'), normal_format1)
            worksheet.write('L31', tools.ustr('5-6'), normal_format1)
            worksheet.write('M30', tools.ustr('4ta'), normal_format1)
            worksheet.write('M31', tools.ustr('6-7'), normal_format1)
            worksheet.write('N30', tools.ustr('5ta'), normal_format1)
            worksheet.write('N31', tools.ustr('7-8'), normal_format1)
            worksheet.write('O30', tools.ustr('6ta'), normal_format1)
            worksheet.write('O31', tools.ustr('8-9'), normal_format1)
            worksheet.write('P30', tools.ustr('7ma'), normal_format1)
            worksheet.write('P31', tools.ustr('9-10'), normal_format1)
            worksheet.write('Q30', tools.ustr('8va'), normal_format1)
            worksheet.write('Q31', tools.ustr('10-11'), normal_format1)
            worksheet.merge_range('R30:S31', tools.ustr('Promedio'), merge_format)

            date_start =  datetime.date(int(lines.date_start.split('-')[0]), int(lines.date_start.split('-')[1]), 1)
            tecnolog_control = self.env['turei_process_control.tecnolog_control_model'].search([('date','=',lines.date_start),('productive_section','=',ps.id),('turn', '=', lines.turn.id)])
            acum_tec_control = self.env['turei_process_control.tecnolog_control_model'].search([('date','>=',date_start),('date','<',lines.date_start),('productive_section','=',ps.id),('turn', '=', lines.turn.id)])
            ttp, trp, ttig, prc, er, sum_time_exog, eo, cdt, ppc, pc, tf, cturnm, cturnt, tt  = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0
            quantity_line = ps.get_efficiency_plan().quantity_line
            h, j, ind_rech, acum_ind_rech = 7, 14, 0.0, 0.0
            for pd in ps.productive_line_ids:
                worksheet.write(24,h, tools.ustr('Ln # ' + pd.name[-2:]), normal_format1)
                worksheet.write(24,j, tools.ustr('Ln # ' + pd.name[-2:]), normal_format1)
                p_cajones, r_caje = 0.0, 0
                for tecn in tecnolog_control:
                    amf = self.env['turei_process_control.rechazo_amf'].search([('tecnolog_control_id', '=', tecn.id),('productive_line_id', '=', pd.id)],limit = 1)
                    p_cajones += amf.produccion_en_cajones
                    r_caje += amf.rechazo_en_cajetijas
                worksheet.write(25,h, p_cajones, normal_format1)
                p_cajones_turn += p_cajones
                worksheet.write(26,h, round(r_caje/500,2), normal_format1)
                r_caje_turn += round(r_caje/500,2)
                worksheet.write(27,h, round((r_caje/500)*100/p_cajones if p_cajones != 0.0 else 0.0 ,2), normal_format1)
                ind_rech += round((r_caje/500)*100/p_cajones if p_cajones != 0.0 else 0.0 ,2)
                h += 1

                for acum in acum_tec_control:
                    amf = self.env['turei_process_control.rechazo_amf'].search([('tecnolog_control_id', '=', acum.id),('productive_line_id', '=', pd.id)],limit = 1)
                    p_cajones += amf.produccion_en_cajones
                    r_caje += amf.rechazo_en_cajetijas
                worksheet.write(25,j, p_cajones, normal_format1)
                p_cajones_turn_acum += p_cajones
                worksheet.write(26,j, round(r_caje/500,2), normal_format1)
                r_caje_turn_acum += round(r_caje/500,2)
                worksheet.write(27,j, round((r_caje/500)*100/p_cajones if p_cajones != 0.0 else 0.0,2), normal_format1)
                acum_ind_rech += round((r_caje/500)*100/p_cajones if p_cajones != 0.0 else 0.0 ,2)
                j += 1
            worksheet.merge_range('H29:I29', round(ind_rech/quantity_line if quantity_line != 0.0 else 0.0,2), normal_format1)
            ind_rech_turn += round(ind_rech/quantity_line if quantity_line != 0.0 else 0.0,2)
            worksheet.merge_range('O29:P29', round(acum_ind_rech/quantity_line if quantity_line != 0.0 else 0.0,2), normal_format1)
            acum_ind_rech_turn += round(acum_ind_rech/quantity_line if quantity_line != 0.0 else 0.0,2)
            general_int, day_values, acum_values, acum1_values = self.env['turei_process_control.interruption.type'].search([]), {}, {}, {}

            for i in xrange(1,9):
                acum_values[i] = 0.0
                acum1_values[i] = 0.0

            for gi in general_int:
                day_values[gi.code] = {'time': 0.0, 'frequency': 0.0}

            for tc in tecnolog_control:
                ttp += tc.plan_time
                # trp += ((tc.production_in_proccess_control * 10000) /tc.productive_capacity) / 60
                pc = tc.productive_section.get_efficiency_plan().productive_capacity
                trp += ((tc.production_in_proccess_control * 10000) / pc) / 60
                prc += tc.production_in_proccess_control
                er += ((tc.production_in_proccess_control * 10000) / (tc.plan_time * 60 * pc) ) * 100
                ppc += tc.production_in_proccess_control
                # pc = tc.productive_capacity
                prom_prod = 0.0
                if tc.attendance_id.name == tools.ustr('Mañana'):
                    x = 1
                    cturnm += 1
                    cturnmt += 1
                else:
                    x = 9
                    cturnt +=1
                    cturntt += 1
                key, key1 = 1, 1
                for ph in tc.production_by_hours_ids:
                   worksheet.write(31, x, ph.production_count, normal_format1)
                   if tc.attendance_id.name == tools.ustr('Mañana'):
                       if key < 9:
                           acum_values[key] = ph.production_count + acum_values[key]
                           acum_values_turn[key] = ph.production_count + acum_values_turn[key]
                           key += 1
                   else:
                       if key1 < 9:
                           acum1_values[key1] = ph.production_count + acum1_values[key1]
                           acum1_values_turn[key1] = ph.production_count + acum1_values_turn[key1]
                           key1 += 1

                   prom_prod += ph.production_count
                   x += 1
                worksheet.merge_range('R32:S32', tools.ustr(round(prom_prod/8,2)), normal_format1)

                for itr in tc.interruptions:
                    if itr.interruption_type.cause == 'exogena':
                        if itr.productive_line_id:
                            sum_time_exog += itr.time
                            ttig += itr.time
                            day_values[itr.interruption_type.code]['time'] = itr.time  + day_values[itr.interruption_type.code]['time']
                        else:
                            sum_time_exog += itr.time * quantity_line#len(ps.productive_line_ids)
                            ttig += itr.time * quantity_line#len(ps.productive_line_ids)
                            day_values[itr.interruption_type.code]['time'] = (itr.time * quantity_line) + day_values[itr.interruption_type.code]['time']
                        day_values[itr.interruption_type.code]['frequency'] = itr.frequency + day_values[itr.interruption_type.code]['frequency']
                        tf += itr.frequency
                        tf_turn += itr.frequency
                    else:
                        if not itr.productive_line_id:
                            ttig += itr.time * quantity_line#len(ps.productive_line_ids)
                        else:
                            ttig += itr.time
                        if itr.interruption_type.code in ['PM','PE','PC']:
                            valor = str(itr.interruption_type.code) + " " + str(itr.machine_id.machine_type_id.name)
                            if valor in day_values:
                                if not itr.productive_line_id:
                                    day_values[valor]['time'] = (itr.time * quantity_line) + day_values[valor]['time']
                                else:
                                    day_values[valor]['time'] = itr.time + day_values[valor]['time']
                                day_values[valor]['frequency'] = itr.frequency + day_values[valor]['frequency']
                                tf += itr.frequency
                                tf_turn += itr.frequency
                            else:
                                day_values[valor] ={'time': 0.0, 'frequency': 0.0}
                                if not itr.productive_line_id:
                                    day_values[valor]['time'] = (itr.time * quantity_line) + day_values[valor]['time']
                                else:
                                    day_values[valor]['time'] = itr.time + day_values[valor]['time']
                                day_values[valor]['frequency'] = itr.frequency + day_values[valor]['frequency']
                                tf += itr.frequency
                                tf_turn += itr.frequency
                        else:
                            if not itr.productive_line_id:
                                day_values[itr.interruption_type.code]['time'] = (itr.time * quantity_line) + day_values[itr.interruption_type.code]['time']
                            else:
                                day_values[itr.interruption_type.code]['time'] = itr.time + day_values[itr.interruption_type.code]['time']
                            day_values[itr.interruption_type.code]['frequency'] = itr.frequency + day_values[itr.interruption_type.code]['frequency']
                            tf += itr.frequency
                            tf_turn += itr.frequency

            div = (ppc * 10000) / (((ttp * 60)- sum_time_exog) * pc) if (((ttp * 60)- sum_time_exog) * pc) != 0.0 else 0.0
            eo = div * 100

            worksheet.merge_range('F5:G5', ttp, normal_format1)
            ttp_turn += ttp
            worksheet.merge_range('F6:G6', round(trp,2), normal_format1)
            trp_turn += trp
            worksheet.merge_range('F7:G7', round((ttig/60)/quantity_line,2), normal_format1)
            ttig_turn += round((ttig/60)/quantity_line,2)
            time_n_j = round(ttp - (trp+(ttig/60)/quantity_line),2)
            worksheet.merge_range('F8:G8', time_n_j, normal_format1)
            tnj_turn += round(ttp - (trp+(ttig/60)/quantity_line),2)
            worksheet.write('H5', (ttp*100)/8, normal_format1)
            ttp_turn_p += (ttp*100)/8
            worksheet.write('H6', round(trp*100/ttp if ttp != 0.0 else 0.0,2), normal_format1)
            trp_turn_p += round(trp*100/ttp if ttp != 0.0 else 0.0,2)
            worksheet.write('H7', round(((ttig/60)/quantity_line)*100/ttp if ttp != 0.0 else 0.0,2), normal_format1)
            ttig_turn_p += round(((ttig/60)/quantity_line)*100/ttp if ttp != 0.0 else 0.0,2)
            worksheet.write('H8', round((ttp - (trp+(ttig/60)/quantity_line))*100/ttp if ttp != 0.0 else 0.0,2), normal_format1)
            tnj_turn_p += round((ttp - (trp+(ttig/60)/quantity_line))*100/ttp if ttp != 0.0 else 0.0,2)

            worksheet.write('R4', len(tecnolog_control), normal_format1)
            tt_turn += len(tecnolog_control)
            worksheet.write('R5', tools.ustr(prc), normal_format1)
            prc_turn += prc
            worksheet.write('R6', prc/len(tecnolog_control) if len(tecnolog_control) != 0.0 else 0.0, normal_format1)
            worksheet.write('R7', round(er/len(tecnolog_control) if len(tecnolog_control) != 0.0 else 0.0,2), normal_format1)
            er_turn += round(er/len(tecnolog_control) if len(tecnolog_control) != 0.0 else 0.0,2)
            worksheet.write('R8', round(eo,2), normal_format1)
            eo_turn += eo
            if time_n_j > 0:
                cdt_real = round(((ttp-((ttig/60)/quantity_line))/ttp)*100 if ttp != 0.0 else 0.0,2)
                cdt_operativo = round(((ttp-(((ttig/60)/quantity_line)-((sum_time_exog/60)/quantity_line)))/ttp)*100 if ttp != 0.0 else 0.0,2)
            else:
                cdt_real = round(((ttp-(((ttig/60)/quantity_line)+time_n_j))/ttp)*100 if ttp != 0.0 else 0.0,2)
                cdt_operativo = round(((ttp-((((ttig/60)/quantity_line)+time_n_j))-((sum_time_exog/60)/quantity_line))/ttp)*100 if ttp != 0.0 else 0.0,2)
            worksheet.write('R9', cdt_real, normal_format1)
            worksheet.write('R10', cdt_operativo, normal_format1)
            cdt_turn += round(((ttp-((ttig/60)/quantity_line))/ttp)*100 if ttp != 0.0 else 0.0,2)

            z = day_values.items()
            z.sort(key=lambda x:(x[1]['time']), reverse=True)
            x = 1
            tt = ((ttig/60)/quantity_line)

            for da in z:
                if da[1]['time'] != 0.0:
                    if da[0] in day_values_turn1:
                        day_values_turn1[da[0]]['frequency'] = day_values_turn1[da[0]]['frequency'] + da[1]['frequency']
                        day_values_turn1[da[0]]['time'] = day_values_turn1[da[0]]['time'] + round(da[1]['time']/60/quantity_line,2)
                    else:
                        day_values_turn1[da[0]]={'time': 0.0, 'frequency': 0.0}
                        day_values_turn1[da[0]]['frequency'] = day_values_turn1[da[0]]['frequency'] + da[1]['frequency']
                        day_values_turn1[da[0]]['time'] = day_values_turn1[da[0]]['time'] + round(da[1]['time']/60/quantity_line,2)

                    worksheet.write(11,x, tools.ustr(da[0]), normal_format1)
                    worksheet.write(12,x, round(da[1]['time']/60/quantity_line,2), normal_format1)
                    worksheet.write(13,x, round(da[1]['frequency'],0), normal_format1)
                    worksheet.write(14,x, round((da[1]['time']/60/quantity_line)*100/tt if tt != 0.0 else 0.0,2), normal_format1)
                    worksheet.write(15,x, round(da[1]['frequency']*100/tf if tf != 0.0 else 0.0,2), normal_format1)

                    x += 1

            for ac in acum_tec_control:
                ttp += ac.plan_time
                pc = ac.productive_section.get_efficiency_plan().productive_capacity
                trp += ((ac.production_in_proccess_control * 10000) /pc) / 60 if pc != 0 else 0.0
                prc += ac.production_in_proccess_control
                er += ((ac.production_in_proccess_control * 10000) / (ac.plan_time * 60 * pc) ) * 100 if (ac.plan_time * 60 * pc) != 0 else 0.0
                ppc += ac.production_in_proccess_control
                # pc = ac.productive_capacity
                key = 1
                key1 = 1
                if ac.attendance_id.name == tools.ustr('Mañana'):
                    cturnm += 1
                    cturnmt1 += 1
                else:
                    cturnt += 1
                    cturntt1 += 1
                for ph in ac.production_by_hours_ids:
                    if ac.attendance_id.name == tools.ustr('Mañana'):
                        if key < 9:
                            acum_values[key] = ph.production_count + acum_values[key]
                            acum_values_turn1[key] = ph.production_count + acum_values_turn1[key]
                            key += 1
                    else:
                        if key1 < 9:
                            acum1_values[key1] = ph.production_count + acum1_values[key1]
                            acum1_values_turn1[key1] = ph.production_count + acum1_values_turn1[key1]
                            key1 += 1

                for it in ac.interruptions:
                    if it.interruption_type.cause == 'exogena':
                        if it.productive_line_id:
                            sum_time_exog += it.time
                            ttig += it.time
                            day_values[it.interruption_type.code]['time'] = it.time + day_values[it.interruption_type.code]['time']
                        else:
                            sum_time_exog += it.time * quantity_line
                            ttig += it.time * quantity_line
                            day_values[it.interruption_type.code]['time'] = (it.time * quantity_line) + day_values[it.interruption_type.code]['time']
                        day_values[it.interruption_type.code]['frequency'] = it.frequency + day_values[it.interruption_type.code]['frequency']
                        tf += it.frequency
                    else:
                        if not it.productive_line_id:
                            ttig += it.time * quantity_line
                        else:
                            ttig += it.time
                        if it.interruption_type.code in ['PM','PE','PC']:
                            valor = str(it.interruption_type.code) + " " + str(it.machine_id.machine_type_id.name)
                            if valor in day_values:
                                if not it.productive_line_id:
                                    day_values[valor]['time'] = (it.time * quantity_line) + day_values[valor]['time']
                                else:
                                    day_values[valor]['time'] = it.time + day_values[valor]['time']
                                day_values[valor]['frequency'] = it.frequency + day_values[valor]['frequency']
                                tf += it.frequency
                            else:
                                day_values[valor] ={'time': 0.0, 'frequency': 0.0}
                                if not it.productive_line_id:
                                    day_values[valor]['time'] = (it.time * quantity_line) + day_values[valor]['time']
                                else:
                                    day_values[valor]['time'] = it.time + day_values[valor]['time']
                                day_values[valor]['frequency'] = it.frequency + day_values[valor]['frequency']
                                tf += it.frequency
                        else:
                            if not it.productive_line_id:
                                day_values[it.interruption_type.code]['time'] = (it.time * quantity_line) + day_values[it.interruption_type.code]['time']
                            else:
                                day_values[it.interruption_type.code]['time'] = it.time + day_values[it.interruption_type.code]['time']
                            day_values[it.interruption_type.code]['frequency'] = it.frequency + day_values[it.interruption_type.code]['frequency']
                            tf += it.frequency

            div = (ppc * 10000) / (((ttp * 60)- sum_time_exog) * pc) if (((ttp * 60)- sum_time_exog) * pc) != 0.0 else 0.0
            eo = div * 100
            tf_turn_acum += tf

            worksheet.merge_range('I5:J5', ttp, normal_format1)
            ttp_turn_acum += ttp
            worksheet.merge_range('I6:J6', round(trp,2), normal_format1)
            trp_turn_acum += round(trp,2)
            worksheet.merge_range('I7:J7', round((ttig/60)/quantity_line,2), normal_format1)
            ttig_turn_acum += round((ttig/60)/quantity_line,2)
            time_n_j_acum = round(ttp - (trp+(ttig/60)/quantity_line),2)
            worksheet.merge_range('I8:J8', time_n_j_acum, normal_format1)
            tnj_turn_acum += round(ttp - (trp+(ttig/60)/quantity_line),2)
            worksheet.write('K5', tools.ustr(100), normal_format1)
            worksheet.write('K6', round(trp*100/ttp if ttp != 0 else 0,2), normal_format1)
            trp_turn_p_acum += round(trp*100/ttp if ttp != 0 else 0,2)
            worksheet.write('K7', round(((ttig/60)/quantity_line)*100/ttp if ttp !=0 else 0,2), normal_format1)
            ttig_turn_p_acum += round(((ttig/60)/quantity_line)*100/ttp if ttp !=0 else 0,2)
            worksheet.write('K8', round((ttp - (trp+(ttig/60)/quantity_line))*100/ttp if ttp !=0 else 0,2), normal_format1)
            tnj_turn_p_acum += round((ttp - (trp+(ttig/60)/quantity_line))*100/ttp if ttp != 0 else 0,2)

            worksheet.write('S4', len(acum_tec_control)+len(tecnolog_control), normal_format1)
            tt_turn_acum += len(acum_tec_control)+len(tecnolog_control)
            worksheet.write('S5', prc, normal_format1)
            prc_acum += prc
            worksheet.write('S6', round(prc/(len(acum_tec_control)+len(tecnolog_control)) if (len(acum_tec_control)+len(tecnolog_control)) != 0 else 0,2), normal_format1)
            worksheet.write('S7', round(er/(len(acum_tec_control)+len(tecnolog_control)) if (len(acum_tec_control)+len(tecnolog_control)) != 0 else 0,2), normal_format1)
            er_turn_acum += round(er/(len(acum_tec_control)+len(tecnolog_control)) if (len(acum_tec_control)+len(tecnolog_control)) != 0 else 0,2)
            worksheet.write('S8', round(eo,2), normal_format1)
            eo_turn_acum += round(eo,2)
            if time_n_j_acum > 0:
                cdt_real_acum = round(((ttp-((ttig/60)/quantity_line))/ttp)*100 if ttp != 0.0 else 0.0,2)
                cdt_operativo_acum = round(((ttp-(((ttig/60)/quantity_line)-((sum_time_exog/60)/quantity_line)))/ttp)*100 if ttp != 0.0 else 0.0,2)
            else:
                cdt_real_acum = round(((ttp-(((ttig/60)/quantity_line)+time_n_j_acum))/ttp)*100 if ttp != 0.0 else 0.0,2)
                cdt_operativo_acum = round(((ttp-((((ttig/60)/quantity_line)+time_n_j_acum))-((sum_time_exog/60)/quantity_line))/ttp)*100 if ttp != 0.0 else 0.0,2)
            worksheet.write('S9', cdt_real_acum, normal_format1)
            worksheet.write('S10', cdt_operativo_acum, normal_format1)
            cdt_turn_acum += round(((ttp-((ttig/60)/quantity_line))/ttp)*100 if ttp != 0 else 0,2)

            z = day_values.items()
            z.sort(key=lambda x:(x[1]['time']),reverse=True)
            x = 1
            tt = ((ttig/60)/quantity_line)
            for da in z:
                if da[1]['time'] != 0.0:
                    if da[0] in day_values_turn2:
                        day_values_turn2[da[0]]['frequency'] = day_values_turn2[da[0]]['frequency'] + da[1]['frequency']
                        day_values_turn2[da[0]]['time'] = day_values_turn2[da[0]]['time'] + round(da[1]['time']/60/quantity_line,2)
                    else:
                        day_values_turn2[da[0]]={'time': 0.0, 'frequency': 0.0}
                        day_values_turn2[da[0]]['frequency'] = day_values_turn2[da[0]]['frequency'] + da[1]['frequency']
                        day_values_turn2[da[0]]['time'] = day_values_turn2[da[0]]['time'] + round(da[1]['time']/60/quantity_line,2)

                    worksheet.write(17,x, da[0], normal_format1)
                    worksheet.write(18,x, round(da[1]['time']/60/quantity_line,2), normal_format1)
                    worksheet.write(19,x, round(da[1]['frequency'],0), normal_format1)
                    worksheet.write(20,x, round((da[1]['time']/60/quantity_line)*100/tt,2), normal_format1)
                    worksheet.write(21,x, round(da[1]['frequency']*100/tf if tf !=0.0 else 0.0,2), normal_format1)
                    x += 1
            y = 9
            prom_acum = 0.0

            for i in xrange(1,9):
                if cturnm != 0:
                    worksheet.write(32, i, round(acum_values[i]/cturnm if cturnm != 0 else 0,2), normal_format1)
                if cturnt != 0:
                    worksheet.write(32, y,round(acum1_values[i]/cturnt if cturnt != 0 else 0,2), normal_format1)
                prom_acum += round(acum1_values[i]/cturnt if cturnt != 0 else 0,2) + round(acum_values[i]/cturnm if cturnm != 0 else 0,2)
                y += 1
            if cturnm != 0 and cturnt != 0:
                worksheet.merge_range('R33:S33', round(prom_acum/16,2), normal_format1)
            elif cturnm == 0 or cturnt == 0:
                worksheet.merge_range('R33:S33', round(prom_acum/8,2), normal_format1)

        worksheet = workbook.add_worksheet(tools.ustr(tools.ustr('Turno: %s') %(lines.turn.name[-1:])))
        worksheet.merge_range('A1:S1', tools.ustr("RESULTADOS ESTADÍSTICOS DE CONTROL DEL PROCESO"), head_format)
        worksheet.merge_range('A2:D2', tools.ustr('Seccion Productiva: TODAS' ), head_format)
        worksheet.merge_range('F2:J2', tools.ustr('Turno: %s') % (lines.turn.name[-1:]), head_format)
        worksheet.merge_range('O2:S2', tools.ustr('Fecha: %s') % (lines.date_start), head_format)

        worksheet.merge_range('A3:E3', tools.ustr('Indicadores'), merge_format)
        worksheet.merge_range('F3:H3', tools.ustr('Día'), merge_format)
        worksheet.merge_range('I3:K3', tools.ustr('Acumulado'), merge_format)
        worksheet.merge_range('A4:E4', tools.ustr('Análisis de utilización del tiempo '), merge_format)
        worksheet.merge_range('F4:G4', tools.ustr('Tiempo (hr)'), merge_format)
        worksheet.write('H4', tools.ustr('%'), merge_format)
        worksheet.merge_range('I4:J4', tools.ustr('Tiempo (hr)'), merge_format)
        worksheet.write('K4', tools.ustr('%'), merge_format)
        worksheet.merge_range('A5:E5', tools.ustr('Tiempo total planificado'), normal_format)
        worksheet.merge_range('A6:E6', tools.ustr('Tiempo real de producción'), normal_format)
        worksheet.merge_range('A7:E7', tools.ustr('Tiempo total de interrupciones generales'), normal_format)
        worksheet.merge_range('A8:E8', tools.ustr('Tiempo no justificado'), normal_format)

        worksheet.merge_range('M3:Q3', tools.ustr('Indicadores'), merge_format)
        worksheet.write('R3', tools.ustr('Día'), merge_format)
        worksheet.write('S3', tools.ustr('Acum'), merge_format)
        worksheet.merge_range('M4:Q4', tools.ustr('Turnos trabajados'), normal_format)
        worksheet.merge_range('M5:Q5', tools.ustr('Producción realizada (cajones)'), normal_format)
        worksheet.merge_range('M6:Q6', tools.ustr('Promedio de cajones/ turno'), normal_format)
        worksheet.merge_range('M7:Q7', tools.ustr('Eficiencia real (%)'), normal_format)
        worksheet.merge_range('M8:Q8', tools.ustr('Eficiencia operativa (%)'), normal_format)
        worksheet.merge_range('M9:Q9', tools.ustr('CDT (%)'), normal_format)

        worksheet.merge_range('A10:S10', tools.ustr('Día'), merge_format)
        worksheet.set_column('A11:A11', 15)

        worksheet.write('A11', tools.ustr('Interrupciones'), normal_format)
        worksheet.write('A12', tools.ustr('Tiempo (hr)'), normal_format)
        worksheet.write('A13', tools.ustr('Frecuencia'), normal_format)
        worksheet.write('A14', tools.ustr('% Tiempo'), normal_format)
        worksheet.write('A15', tools.ustr('% Frecuencia'), normal_format)

        worksheet.merge_range('A16:S16', tools.ustr('Acumulado'), merge_format)

        worksheet.write('A17', tools.ustr('Interrupciones'), normal_format)
        worksheet.write('A18', tools.ustr('Tiempo (hr)'), normal_format)
        worksheet.write('A19', tools.ustr('Frecuencia'), normal_format)
        worksheet.write('A20', tools.ustr('% Tiempo'), normal_format)
        worksheet.write('A21', tools.ustr('% Frecuencia'), normal_format)

        worksheet.merge_range('A22:S22', tools.ustr('Producción y Rechazo de las AMF'), merge_format)
        worksheet.merge_range('D23:G23', tools.ustr('Día'), merge_format)
        worksheet.merge_range('H23:I23', tools.ustr('Brigada'), merge_format)
        worksheet.merge_range('D24:G24', tools.ustr('Indicadores'), normal_format)
        worksheet.merge_range('D25:G25', tools.ustr('Producción (cajones)'), normal_format)
        worksheet.merge_range('D26:G26', tools.ustr('Rechazo (cajones)'), normal_format)
        worksheet.merge_range('D27:G27', tools.ustr('Índice de Rechazo Ln (%)'), normal_format)
        worksheet.merge_range('D28:G28', tools.ustr('Índice de Rechazo B (%)'), normal_format)

        worksheet.merge_range('K23:N23', tools.ustr('Acumulado'), merge_format)
        worksheet.merge_range('O23:P23', tools.ustr('Brigada'), merge_format)
        worksheet.merge_range('K24:N24', tools.ustr('Indicadores'), normal_format)
        worksheet.merge_range('K25:N25', tools.ustr('Producción (cajones)'), normal_format)
        worksheet.merge_range('K26:N26', tools.ustr('Rechazo (cajones)'), normal_format)
        worksheet.merge_range('K27:N27', tools.ustr('Índice de Rechazo Ln (%)'), normal_format)
        worksheet.merge_range('K28:N28', tools.ustr('Índice de Rechazo B (%)'), normal_format)

        worksheet.merge_range('A29:A30', tools.ustr('Indicadores'), merge_format)
        worksheet.write('A31', tools.ustr('Día'), normal_format)
        worksheet.write('A32', tools.ustr('Acumulado'), normal_format)
        worksheet.write('B29', tools.ustr('1era'), normal_format1)
        worksheet.write('B30', tools.ustr('7-8'), normal_format1)
        worksheet.write('C29', tools.ustr('2da'), normal_format1)
        worksheet.write('C30', tools.ustr('8-9'), normal_format1)
        worksheet.write('D29', tools.ustr('3era'), normal_format1)
        worksheet.write('D30', tools.ustr('9-10'), normal_format1)
        worksheet.write('E29', tools.ustr('4ta'), normal_format1)
        worksheet.write('E30', tools.ustr('10-11'), normal_format1)
        worksheet.write('F29', tools.ustr('5ta'), normal_format1)
        worksheet.write('F30', tools.ustr('11-12'), normal_format1)
        worksheet.write('G29', tools.ustr('6ta'), normal_format1)
        worksheet.write('G30', tools.ustr('12-1'), normal_format1)
        worksheet.write('H29', tools.ustr('7ma'), normal_format1)
        worksheet.write('H30', tools.ustr('1-2'), normal_format1)
        worksheet.write('I29', tools.ustr('8va'), normal_format1)
        worksheet.write('I30', tools.ustr('2-3'), normal_format1)

        worksheet.write('J29', tools.ustr('1era'), normal_format1)
        worksheet.write('J30', tools.ustr('3-4'), normal_format1)
        worksheet.write('K29', tools.ustr('2da'), normal_format1)
        worksheet.write('K30', tools.ustr('4-5'), normal_format1)
        worksheet.write('L29', tools.ustr('3era'), normal_format1)
        worksheet.write('L30', tools.ustr('5-6'), normal_format1)
        worksheet.write('M29', tools.ustr('4ta'), normal_format1)
        worksheet.write('M30', tools.ustr('6-7'), normal_format1)
        worksheet.write('N29', tools.ustr('5ta'), normal_format1)
        worksheet.write('N30', tools.ustr('7-8'), normal_format1)
        worksheet.write('O29', tools.ustr('6ta'), normal_format1)
        worksheet.write('O30', tools.ustr('8-9'), normal_format1)
        worksheet.write('P29', tools.ustr('7ma'), normal_format1)
        worksheet.write('P30', tools.ustr('9-10'), normal_format1)
        worksheet.write('Q29', tools.ustr('8va'), normal_format1)
        worksheet.write('Q30', tools.ustr('10-11'), normal_format1)
        worksheet.merge_range('R29:S30', tools.ustr('Promedio'), merge_format)

        worksheet.write(24,7, p_cajones_turn, normal_format1)
        worksheet.write(25,7, r_caje_turn, normal_format1)
        worksheet.write(26,7, round(ind_rech_turn/19,2), normal_format1)

        worksheet.write(24,14, p_cajones_turn_acum, normal_format1)
        worksheet.write(25,14, r_caje_turn_acum, normal_format1)
        worksheet.write(26,14, round(acum_ind_rech_turn/19,2), normal_format1)

        worksheet.merge_range('H28:I28', round(ind_rech_turn/10,2), normal_format1)
        worksheet.merge_range('O28:P28', round(acum_ind_rech_turn/10,2), normal_format1)

        worksheet.merge_range('F5:G5', ttp_turn, normal_format1)
        worksheet.merge_range('F6:G6', round(trp_turn, 2), normal_format1)
        worksheet.merge_range('F7:G7', ttig_turn, normal_format1)
        worksheet.merge_range('F8:G8', tnj_turn, normal_format1)
        worksheet.write('H5', round(ttp_turn_p/10,2), normal_format1)
        worksheet.write('H6', round(trp_turn_p/10,2), normal_format1)
        worksheet.write('H7', round(ttig_turn_p/10,2), normal_format1)
        worksheet.write('H8', round(tnj_turn_p/10,2), normal_format1)

        worksheet.write('R4', tools.ustr(tt_turn), normal_format1)
        worksheet.write('R5', tools.ustr(prc_turn), normal_format1)
        pct = prc_turn/tt_turn if tt_turn != 0 else 0.0
        worksheet.write('R6', round(pct,2), normal_format1)
        worksheet.write('R7', round(er_turn/tt_turn if tt_turn != 0 else 0.0,2), normal_format1)
        worksheet.write('R8', round(eo_turn/tt_turn if tt_turn != 0 else 0.0,2), normal_format1)
        worksheet.write('R9', round(cdt_turn/tt_turn if tt_turn != 0 else 0.0,2), normal_format1)

        worksheet.merge_range('I5:J5', ttp_turn_acum, normal_format1)
        worksheet.merge_range('I6:J6', trp_turn_acum, normal_format1)
        worksheet.merge_range('I7:J7', ttig_turn_acum, normal_format1)
        worksheet.merge_range('I8:J8', tnj_turn_acum, normal_format1)

        worksheet.write('K6', round(trp_turn_p_acum/10,2), normal_format1)
        worksheet.write('K7', round(ttig_turn_p_acum/10,2), normal_format1)
        worksheet.write('K8', round(tnj_turn_p_acum/10,2), normal_format1)
        worksheet.write('S4', tt_turn_acum, normal_format1)
        worksheet.write('S5', prc_acum, normal_format1)
        worksheet.write('S6', round(prc_acum/tt_turn_acum if tt_turn_acum != 0 else 0,2), normal_format1)
        worksheet.write('S7', round(er_turn_acum/10,2), normal_format1)
        worksheet.write('S8', round(eo_turn_acum/10,2), normal_format1)
        worksheet.write('S9', round(cdt_turn_acum/10,2), normal_format1)

        z = day_values_turn1.items()
        z.sort(key=lambda x: (x[1]['time']), reverse=True)
        x = 1
        for da in z:
            if da[1]['time'] != 0.0:
                worksheet.write(10, x, tools.ustr(da[0]), normal_format1)
                worksheet.write(11, x, round(da[1]['time'], 2), normal_format1)
                worksheet.write(12, x, round(da[1]['frequency'], 0), normal_format1)
                worksheet.write(13, x, round((da[1]['time'] * 100) / ttig_turn if ttig_turn != 0.0 else 0.0, 2), normal_format1)
                worksheet.write(14, x, round(da[1]['frequency'] * 100 / tf_turn if tf_turn != 0.0 else 0.0, 2), normal_format1)
                x += 1

        z = day_values_turn2.items()
        z.sort(key=lambda x: (x[1]['time']), reverse=True)
        x = 1

        for da in z:
            if da[1]['time'] != 0.0:
                worksheet.write(16, x, tools.ustr(da[0]), normal_format1)
                worksheet.write(17, x, round(da[1]['time'], 2), normal_format1)
                worksheet.write(18, x, round(da[1]['frequency'], 0), normal_format1)
                worksheet.write(19, x, round((da[1]['time'] * 100) / ttig_turn_acum if ttig_turn_acum != 0.0 else 0.0, 2), normal_format1)
                worksheet.write(20, x, round(da[1]['frequency'] * 100 / tf_turn_acum if tf_turn_acum != 0.0 else 0.0, 2), normal_format1)
                x += 1

        y = 9
        prom_acum = 0.0

        for i in xrange(1, 9):
            if cturnmt != 0:
                worksheet.write(30, i, round(acum_values_turn[i]/cturnmt if cturnmt != 0 else 0, 2), normal_format1)
            if cturntt != 0:
                worksheet.write(30, y, round(acum1_values_turn[i]/cturntt if cturntt != 0 else 0, 2), normal_format1)
            prom_acum += round(acum1_values_turn[i]/cturntt if cturntt != 0 else 0, 2) + round(
                acum_values_turn[i]/cturnmt if cturnmt != 0 else 0, 2)
            y += 1
        if cturnmt != 0 and cturntt != 0:
            worksheet.merge_range('R31:S31', round(prom_acum / 16, 2), normal_format1)
        elif cturnmt == 0 or cturntt == 0:
            worksheet.merge_range('R31:S31', round(prom_acum / 8, 2), normal_format1)

        y = 9
        prom_acum = 0.0

        for i in xrange(1, 9):
            if cturnmt1 != 0:
                worksheet.write(31, i, round(acum_values_turn1[i]/cturnmt1 if cturnmt1 != 0 else 0, 2), normal_format1)
            if cturntt1 != 0:
                worksheet.write(31, y, round(acum1_values_turn1[i]/cturntt1 if cturntt1 != 0 else 0, 2), normal_format1)
            prom_acum += round(acum1_values_turn1[i]/cturntt1 if cturntt1 != 0 else 0, 2) + round(
                acum_values_turn1[i]/cturnmt1 if cturnmt1 != 0 else 0, 2)
            y += 1
        if cturnmt1 != 0 and cturntt1 != 0:
            worksheet.merge_range('R32:S32', round(prom_acum / 16, 2), normal_format1)
        elif cturnmt1 == 0 or cturntt1 == 0:
            worksheet.merge_range('R32:S32', round(prom_acum / 8, 2), normal_format1)

StatisticalResultsToExcelReport('report.turei_process_control.statistical_results_report', 'wzd.statistical.results.to.excel')
