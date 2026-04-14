# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class EfficiencyLtrToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        date_start = datetime.date(int(lines.date_start.split('-')[0]), int(lines.date_start.split('-')[1]), 1)

        tecnolog_control = self.env['process_control_tobacco.tecnolog_control_model'].search([('date', '=', lines.date_start), ('turn', '=', lines.turn.id)])
        acum_tec_control = self.env['process_control_tobacco.tecnolog_control_model'].search([('date', '>=', date_start), ('date', '<', lines.date_start), ('turn', '=', lines.turn.id)])

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        normal_format1 = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        worksheet = workbook.add_worksheet(tools.ustr(tools.ustr('Eficiencia DTR')))
        worksheet.merge_range('A1:S1', tools.ustr("REPORTE DE EFICIENCIA DEL DEPTO. DE PRODUCCION DE TABACO RECONSTITUIDO"), head_format)

        worksheet.merge_range('F2:J2', tools.ustr('Turno: %s') % (lines.turn.turn.name[-1:]), head_format)

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
        worksheet.merge_range('M5:Q5', tools.ustr('Producción realizada (kg)'), normal_format)
        worksheet.merge_range('M6:Q6', tools.ustr('Promedio de kg/turno'), normal_format)
        worksheet.merge_range('M7:Q7', tools.ustr('Flujo L 100'), normal_format)
        worksheet.merge_range('M8:Q8', tools.ustr('Flujo L 300'), normal_format)
        worksheet.merge_range('M9:Q9', tools.ustr('Eficiencia real (%)'), normal_format)
        worksheet.merge_range('M10:Q10', tools.ustr('Eficiencia operativa (%)'), normal_format)
        worksheet.merge_range('M11:Q11', tools.ustr('CDT real(%)'), normal_format)
        worksheet.merge_range('M12:Q12', tools.ustr('CDT operativo(%)'), normal_format)

        worksheet.merge_range('A14:S14', tools.ustr('Día'), merge_format)
        worksheet.set_column('A15:A15', 15)

        worksheet.write('A15', tools.ustr('Interrupciones'), normal_format)
        worksheet.write('A16', tools.ustr('Tiempo (hr)'), normal_format)
        worksheet.write('A17', tools.ustr('Frecuencia'), normal_format)
        worksheet.write('A18', tools.ustr('% Tiempo'), normal_format)
        worksheet.write('A19', tools.ustr('% Frecuencia'), normal_format)

        worksheet.merge_range('A21:S21', tools.ustr('Acumulado'), merge_format)

        worksheet.write('A22', tools.ustr('Interrupciones'), normal_format)
        worksheet.write('A23', tools.ustr('Tiempo (hr)'), normal_format)
        worksheet.write('A24', tools.ustr('Frecuencia'), normal_format)
        worksheet.write('A25', tools.ustr('% Tiempo'), normal_format)
        worksheet.write('A26', tools.ustr('% Frecuencia'), normal_format)

        worksheet.merge_range('A28:A29', tools.ustr('Indicadores'), merge_format)
        worksheet.write('A30', tools.ustr('Día'), normal_format)
        worksheet.write('A31', tools.ustr('Acumulado'), normal_format)
        worksheet.write('B28', tools.ustr('1era'), normal_format1)
        worksheet.write('B29', tools.ustr('7-8'), normal_format1)
        worksheet.write('C28', tools.ustr('2da'), normal_format1)
        worksheet.write('C29', tools.ustr('8-9'), normal_format1)
        worksheet.write('D28', tools.ustr('3era'), normal_format1)
        worksheet.write('D29', tools.ustr('9-10'), normal_format1)
        worksheet.write('E28', tools.ustr('4ta'), normal_format1)
        worksheet.write('E29', tools.ustr('10-11'), normal_format1)
        worksheet.write('F28', tools.ustr('5ta'), normal_format1)
        worksheet.write('F29', tools.ustr('11-12'), normal_format1)
        worksheet.write('G28', tools.ustr('6ta'), normal_format1)
        worksheet.write('G29', tools.ustr('12-1'), normal_format1)
        worksheet.write('H28', tools.ustr('7ma'), normal_format1)
        worksheet.write('H29', tools.ustr('1-2'), normal_format1)
        worksheet.write('I28', tools.ustr('8va'), normal_format1)
        worksheet.write('I29', tools.ustr('2-3'), normal_format1)

        worksheet.write('J28', tools.ustr('1era'), normal_format1)
        worksheet.write('J29', tools.ustr('3-4'), normal_format1)
        worksheet.write('K28', tools.ustr('2da'), normal_format1)
        worksheet.write('K29', tools.ustr('4-5'), normal_format1)
        worksheet.write('L28', tools.ustr('3era'), normal_format1)
        worksheet.write('L29', tools.ustr('5-6'), normal_format1)
        worksheet.write('M28', tools.ustr('4ta'), normal_format1)
        worksheet.write('M29', tools.ustr('6-7'), normal_format1)
        worksheet.write('N28', tools.ustr('5ta'), normal_format1)
        worksheet.write('N29', tools.ustr('7-8'), normal_format1)
        worksheet.write('O28', tools.ustr('6ta'), normal_format1)
        worksheet.write('O29', tools.ustr('8-9'), normal_format1)
        worksheet.write('P28', tools.ustr('7ma'), normal_format1)
        worksheet.write('P29', tools.ustr('9-10'), normal_format1)
        worksheet.write('Q28', tools.ustr('8va'), normal_format1)
        worksheet.write('Q29', tools.ustr('10-11'), normal_format1)
        worksheet.merge_range('R28:S29', tools.ustr('Promedio'), merge_format)

        ttp, rp, tti, tpexo, tpend, tf = 0, 0.0, 0.0, 0.0, 0.0, 0
        for tc in tecnolog_control:
            ttp += tc.plan_time
            rp += tc.reconstituted_produced
            for it in tc.interruptions:
                tti += it.time
                tf += it.frequency
                if it.interruption_type.cause == 'exogena':
                    tpexo += it.time
                if it.interruption_type.cause == 'endogena':
                    tpend += it.time

        worksheet.merge_range('F5:G5', ttp, normal_format)
        worksheet.write('H5', 100, normal_format)
        trp = (rp/400)/60
        worksheet.merge_range('F6:G6', round(trp,2), normal_format)
        worksheet.write('H6', round(trp*100/ttp,2), normal_format)
        worksheet.merge_range('F7:G7', round(tti/60, 2), normal_format)
        worksheet.write('H7', round((tti/60) * 100 / ttp, 2), normal_format)
        tnj = ttp -((trp+tti) / 60)
        worksheet.merge_range('F8:G8', round(tnj, 2), normal_format)
        worksheet.write('H8', round(tnj * 100 / ttp, 2), normal_format)
        worksheet.write('R4', len(tecnolog_control), merge_format)
        worksheet.write('R5', rp, merge_format)
        worksheet.write('R6', rp/len(tecnolog_control), merge_format)
        worksheet.write('R7', round(tecnolog_control.quantity_vena_polvo/tecnolog_control.execution_time_l100,2), merge_format)
        worksheet.write('R8', round(tecnolog_control.quantity_vena_polvo / tecnolog_control.execution_time_l300, 2), merge_format)
        efficienty_real = rp / (ttp * tecnolog_control.productive_capacity)*100
        worksheet.write('R9', round(efficienty_real, 2), merge_format)
        efficienty_operativy = rp / (ttp - tpexo) * tecnolog_control.productive_capacity * 100
        worksheet.write('R10', round(efficienty_operativy, 2), merge_format)
        cdt_real = ttp - tti / ttp * 100
        worksheet.write('R11', round(cdt_real, 2), merge_format)
        cdt_operativy = ttp - tpexo / ttp * 100
        worksheet.write('R12', round(cdt_operativy, 2), merge_format)

        interuction = self.env['process_control_tobacco.interruption.type'].search([])
        day_values = {}

        for value in interuction:
            day_values[value.code] = {'time': 0.0, 'frequency': 0.0}

        for itr in tecnolog_control.interruptions:
            if itr.interruption_type.code in ['PM', 'PE', 'PC']:
                valor = str(itr.interruption_type.code) + " " + str(itr.machine_type_id.name)
                if valor in day_values:
                    day_values[valor]['time'] = itr.time + day_values[valor]['time']
                    day_values[valor]['frequency'] = itr.frequency + day_values[valor]['frequency']
                else:
                    day_values[valor] = {'time': 0.0, 'frequency': 0.0}
                    day_values[valor]['time'] = itr.time + day_values[valor]['time']
                    day_values[valor]['frequency'] = itr.frequency + day_values[valor]['frequency']
            else:
                day_values[itr.interruption_type.code]['time'] = itr.time + day_values[itr.interruption_type.code]['time']
                day_values[itr.interruption_type.code]['frequency'] = itr.frequency + day_values[itr.interruption_type.code]['frequency']

        z = day_values.items()
        z.sort(key=lambda x: (x[1]['time']), reverse=True)
        x = 1
        for da in z:
            if da[1]['time'] != 0.0:
                worksheet.write(14, x, tools.ustr(da[0]), normal_format1)
                worksheet.write(15, x, round(da[1]['time'] / 60, 2), normal_format1)
                worksheet.write(16, x, da[1]['frequency'], normal_format1)
                worksheet.write(17, x, round((da[1]['time'] / 60) * 100 / (tti / 60) if tti != 0.0 else 0.0, 2), normal_format1)
                worksheet.write(18, x, round(da[1]['frequency'] * 100 / tf if tf != 0 else 0, 2), normal_format1)
                x += 1

        ttp_a, rp_a, tti_a, tpexo_a, tpend_a = 0, 0.0, 0.0, 0.0, 0.0
        qvp_a, etl100, etl300, tf_a = 0.0, 0.0, 0.0, 0

        acum_values, acum1_values = {},{}
        for i in xrange(1, 9):
            acum_values[i] = 0.0
        for e in xrange(9,17):
            acum1_values[e] = 0.0

        prod_count = 0
        if tecnolog_control.attendance_id.name == tools.ustr('Mañana'):
            x = 1
        else:
            x = 9
        for pbh in tecnolog_control.production_by_hours_ids:
            prod_count += pbh.production_count
            worksheet.write(29, x, pbh.production_count, normal_format1)
            if tecnolog_control.attendance_id.name == tools.ustr('Mañana'):
                acum_values[x] = pbh.production_count + acum_values[x]
            else:
                acum1_values[x] = pbh.production_count + acum1_values[x]
            x += 1

        worksheet.merge_range('R30:S30', round(prod_count / len(tecnolog_control.production_by_hours_ids), 2), normal_format)
        flag, flag1 = False, False
        for acum in acum_tec_control:
            if acum.attendance_id.name == tools.ustr('Mañana'):
                x = 1
                flag = True
                for prod in acum.production_by_hours_ids:
                    acum_values[x] = prod.production_count + acum_values[x]
                    x += 1
            else:
                x = 9
                flag1 = True
                for prod in acum.production_by_hours_ids:
                    acum1_values[x] = prod.production_count + acum1_values[x]
                    x += 1

            ttp_a += acum.plan_time
            rp_a += acum.reconstituted_produced
            qvp_a += acum.quantity_vena_polvo
            etl100 += acum.execution_time_l100
            etl300 += acum.execution_time_l300
            for it_acum in acum.interruptions:
                tti_a += it_acum.time
                tf_a += it_acum.frequency
                if it_acum.interruption_type.cause == 'exogena':
                    tpexo_a += it_acum.time
                if it_acum.interruption_type.cause == 'endogena':
                    tpend_a += it_acum.time

                if it_acum.interruption_type.code in ['PM', 'PE', 'PC']:
                    valor = str(it_acum.interruption_type.code) + " " + str(it_acum.machine_type_id.name)
                    if valor in day_values:
                        day_values[valor]['time'] = it_acum.time + day_values[valor]['time']
                        day_values[valor]['frequency'] = it_acum.frequency + day_values[valor]['frequency']
                    else:
                        day_values[valor] = {'time': 0.0, 'frequency': 0.0}
                        day_values[valor]['time'] = it_acum.time + day_values[valor]['time']
                        day_values[valor]['frequency'] = it_acum.frequency + day_values[valor]['frequency']
                else:
                    day_values[it_acum.interruption_type.code]['time'] = it_acum.time + day_values[it_acum.interruption_type.code]['time']
                    day_values[it_acum.interruption_type.code]['frequency'] = it_acum.frequency + day_values[it_acum.interruption_type.code]['frequency']

        za = day_values.items()
        za.sort(key=lambda x: (x[1]['time']), reverse=True)
        x = 1
        tti_g = (tti + tti_a)/60
        tf_g = tf + tf_a
        for da in za:
            if da[1]['time'] != 0.0:
                worksheet.write(21, x, tools.ustr(da[0]), normal_format1)
                worksheet.write(22, x, round(da[1]['time'] / 60, 2), normal_format1)
                worksheet.write(23, x, da[1]['frequency'], normal_format1)
                worksheet.write(24, x, round((da[1]['time'] / 60) * 100 / tti_g if tti_g != 0.0 else 0.0, 2), normal_format1)
                worksheet.write(25, x, round(da[1]['frequency'] * 100 / tf_g if tf_g != 0 else 0, 2), normal_format1)
                x += 1

        worksheet.merge_range('I5:J5', ttp_a + ttp, normal_format)
        worksheet.write('K5', 100, normal_format)
        trp_a = (rp_a / 400) / 60
        worksheet.merge_range('I6:J6', round(trp_a + trp, 2), normal_format)
        worksheet.write('K6', round((trp_a + trp)*100/(ttp_a + ttp),2), normal_format)
        worksheet.merge_range('I7:J7', round((tti_a + tti) / 60, 2), normal_format)
        worksheet.write('K7', round(((tti_a + tti) / 60) * 100 / (ttp_a + ttp), 2), normal_format)
        ttp_a1 = ttp_a + ttp
        trp_a1 = trp_a + trp
        tti_a1 = tti_a + tti
        tnj_a = ttp_a1 - ((trp_a1 + tti_a1) / 60)
        worksheet.merge_range('I8:J8', round(tnj_a, 2), normal_format)
        worksheet.write('K8', round(tnj_a * 100 / ttp_a1, 2), normal_format)
        worksheet.write('S4', len(acum_tec_control)+len(tecnolog_control), merge_format)
        worksheet.write('S5', rp_a + rp, merge_format)
        rp_a1 = rp_a + rp
        long = len(acum_tec_control) + len(tecnolog_control)
        worksheet.write('S6', rp_a1 / long, merge_format)
        qvp_a1 = qvp_a + tecnolog_control.quantity_vena_polvo
        et1 = etl100 + tecnolog_control.execution_time_l100
        worksheet.write('S7', round(qvp_a1 / et1, 2), merge_format)
        et3 = etl300 + tecnolog_control.execution_time_l300
        worksheet.write('S8', round(qvp_a1 / et3, 2), merge_format)
        efficienty_real_a = rp_a1 / (ttp_a1 * tecnolog_control.productive_capacity) * 100
        worksheet.write('S9', round(efficienty_real_a, 2), merge_format)
        efficienty_operativy_a = rp_a1 / (ttp_a1 - (tpexo_a + tpexo)) * tecnolog_control.productive_capacity * 100
        worksheet.write('S10', round(efficienty_operativy_a, 2), merge_format)
        cdt_real_a = ttp_a1 - tti_a1 / ttp_a1 * 100
        worksheet.write('S11', round(cdt_real_a, 2), merge_format)
        cdt_operativy_a = ttp_a1 - (tpexo_a + tpexo) / ttp_a1 * 100
        worksheet.write('S12', round(cdt_operativy_a, 2), merge_format)

        cont, sum = 0, 0
        if flag:
            for i in xrange(1,9):
                worksheet.write(30, i, acum_values[i], normal_format1)
                cont += 1
                sum += acum_values[i]
        if flag1:
            for i in xrange(9,17):
                worksheet.write(30, i, acum1_values[i], normal_format1)
                cont += 1
                sum += acum1_values[i]
        worksheet.merge_range('R31:S31', round(sum / cont if cont != 0 else 0, 2), normal_format)


























EfficiencyLtrToExcelReport('report.process_control_tobacco.efficiency_ltr_report', 'wzd.efficiency.ltr.to.excel')
