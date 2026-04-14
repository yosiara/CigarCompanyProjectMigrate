# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class TimeUseToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        query = """SELECT
                    CAST("date" as VARCHAR) || CAST(productive_section as VARCHAR) || CAST(turn as VARCHAR) AS key,
                    date,
                    productive_section,
                    turn,
                    cause,
                    "public".turei_process_control_interruption.productive_line_id as productive_line,
                    frequency AS total_frequency,
                    "time" AS total_time,
                    interruption_type,
                    productive_capacity AS  productive_capacity,
                    plan_time AS plan_time,
                    production_in_proccess_control AS production_done
                FROM
                    "public".turei_process_control_interruption
                INNER JOIN "public".turei_process_control_tecnolog_control_model ON "public".turei_process_control_interruption.tec_control_model = "public".turei_process_control_tecnolog_control_model."id"
                INNER JOIN "public".turei_process_control_interruption_type ON "public".turei_process_control_interruption.interruption_type = "public".turei_process_control_interruption_type."id"
                WHERE
                    "date" BETWEEN '%s'
                AND '%s'
                ORDER BY "key", productive_section, "date", turn"""

        query %= (lines.date_start, lines.date_end)

        self.env.cr.execute(query)
        records_query = self.env.cr.dictfetchall()

        if not records_query:
            self.env.user.notify_info(tools.ustr('No existen datos que mostrar.'))
            return

        records = dict()

        i = 0
        key_last = '-1'
        count = 0

        for i in range(0, len(records_query)):
            if key_last != records_query[i]['key']:
                count = 1
                records.update({records_query[i]['key']: records_query[i]})
                records[records_query[i]['key']].update({'endogena': records_query[i]['total_time'] if records_query[i]['cause'] == 'endogena' else 0.00,
                                                         'exogena': records_query[i]['total_time'] if records_query[i]['cause'] == 'exogena' else 0.00,
                                                         'count': count,
                                                         'count_lines': len(
                                                             self.env['turei_process_control.productive_section'].search([('id', '=', records_query[i]['productive_section'])]).productive_line_ids)
                                                         })
                if not records_query[i]['productive_line']:
                    records[records_query[i]['key']]['total_time'] = records[records_query[i]['key']]['total_time'] * records[records_query[i]['key']]['count_lines']
                    if records_query[i]['cause'] == 'endogena':
                        records[records_query[i]['key']]['endogena'] = records[records_query[i]['key']]['endogena']
                    if records_query[i]['cause'] == 'exogena':
                        records[records_query[i]['key']]['exogena'] = records[records_query[i]['key']]['exogena'] * records[records_query[i]['key']]['count_lines']

                key_last = records_query[i]['key']
            else:
                count += 1
                records[records_query[i]['key']]['plan_time'] += records_query[i]['plan_time']
                records[records_query[i]['key']]['production_done'] += records_query[i]['production_done']
                records[records_query[i]['key']]['productive_capacity'] += records_query[i]['productive_capacity']
                records[records_query[i]['key']]['total_frequency'] += records_query[i]['total_frequency']

                if not records_query[i]['productive_line']:
                    records[records_query[i]['key']]['total_time'] += records_query[i]['total_time'] * records[records_query[i]['key']]['count_lines']
                    if records_query[i]['cause'] == 'endogena':
                        records[records_query[i]['key']]['endogena'] += records_query[i]['total_time']
                    if records_query[i]['cause'] == 'exogena':
                        records[records_query[i]['key']]['exogena'] += records_query[i]['total_time'] * records[records_query[i]['key']]['count_lines']
                else:
                    records[records_query[i]['key']]['total_time'] += records_query[i]['total_time']
                    records[records_query[i]['key']]['endogena'] += records_query[i]['total_time'] if records_query[i]['cause'] == 'endogena' else 0.00
                    records[records_query[i]['key']]['exogena'] += records_query[i]['total_time'] if records_query[i]['cause'] == 'exogena' else 0.00
                records[records_query[i]['key']]['count'] = count

        worksheet = workbook.add_worksheet(tools.ustr("Utilización del tiempo"))
        worksheet.set_column('B:M', 23)
        worksheet.set_column('F4:F4', 30)
        worksheet.set_column('I4:I4', 30)
        worksheet.set_column('G4:G4', 30)
        worksheet.set_column('H4:H4', 30)
        worksheet.set_column('K4:M4', 30)

        fecha_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        fecha_data_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter'})

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        data_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})

        worksheet.write('B3', 'Desde', merge_format)
        worksheet.write('C3', lines.date_start, fecha_format)
        worksheet.write('D3', 'Hasta', merge_format)
        worksheet.write('E3', lines.date_end, fecha_format)

        worksheet.write('B4', tools.ustr('Año'), merge_format)
        worksheet.write('C4', tools.ustr('Mes'), merge_format)
        worksheet.write('D4', tools.ustr('Día'), merge_format)
        worksheet.write('E4', tools.ustr('Turno'), merge_format)
        worksheet.write('F4', tools.ustr('Sección Productiva'), merge_format)
        worksheet.write('G4', tools.ustr('Tiempo Total Planificado'), merge_format)
        worksheet.write('H4', tools.ustr('Tiempo Real Trabajado'), merge_format)
        worksheet.write('I4', tools.ustr('Tiempo Total de Interrupciones'), merge_format)
        worksheet.write('J4', tools.ustr('Tiempo no Justificado'), merge_format)
        worksheet.write('K4', tools.ustr('Tiempo perdido \n por causas exógenas'), merge_format)
        worksheet.write('L4', tools.ustr('Tiempo Perdido \n por Causas Endógenas'), merge_format)

        aux_row = 4
        records = records.items()
        records.sort()

        for c_model in records:
            aux_row += 1
            date = fields.datetime.strptime(c_model[1].get('date'), DEFAULT_SERVER_DATE_FORMAT)
            worksheet.write_number('B' + str(aux_row), date.year, fecha_data_format)
            worksheet.write_number('C' + str(aux_row), date.month, fecha_data_format)
            worksheet.write_number('D' + str(aux_row), date.day, fecha_data_format)
            worksheet.write('E' + str(aux_row), self.env['resource.calendar'].search([('id', '=', c_model[1].get('turn'))], limit=1).name, data_format)
            worksheet.write('F' + str(aux_row), self.env['turei_process_control.productive_section'].search([('id', '=', c_model[1].get('productive_section'))], limit=1).name, data_format)

            # •	Tiempo Total Planificado (horas) = ∑de todos los tiempos planificados) / 60 minutos
            plan_time = c_model[1].get('plan_time') / float(c_model[1].get('count'))
            worksheet.write('G' + str(aux_row), plan_time, data_format)
            # •	Tiempo Real de Producción (horas) = Producción realizada*10000 / Capacidad productiva) / 60 minutos
            real_production_time = c_model[1].get('production_done') * 10000.0 / (c_model[1].get('productive_capacity')) / 60.00
            real_production_time_str = str(real_production_time).split('.')
            worksheet.write('H' + str(aux_row), real_production_time_str[0]+'.'+real_production_time_str[1][:2], data_format)
            # •	Tiempo Total de Interrupciones (horas) = ∑todos los tiempos de interrupciones ocurridas / 60 minutos
            total_time = float(c_model[1].get('total_time')) / 60.00/ 2

            total_time_str = str(total_time).split('.')
            #worksheet.write('I' + str(aux_row), total_time_str[0]+'.'+total_time_str[1][:2], data_format)
            # •	Tiempo no justificado (horas) = Tiempo Total Planificado – (Tiempo Real de Producción + Tiempo Total de Interrupciones) / 60 min
            time_no_justify = plan_time - (real_production_time + total_time)
            time_no_justify_str = str(time_no_justify).split('.')
            worksheet.write('J' + str(aux_row), time_no_justify_str[0]+'.'+time_no_justify_str[1][:2], data_format)
            exo_time = str(c_model[1].get('exogena') / 60.00/2).split('.')
            worksheet.write('K' + str(aux_row), exo_time[0]+'.'+exo_time[1][:2], data_format)
            endo_time = str(c_model[1].get('endogena') / 60.00/2).split('.')
            worksheet.write('L' + str(aux_row), endo_time[0]+'.'+endo_time[1][:2], data_format)
            tti = round((c_model[1].get('exogena') / 60.00/2) + (c_model[1].get('endogena') / 60.00/2),2)
            worksheet.write('I' + str(aux_row), round(total_time,2), data_format)


TimeUseToExcelReport('report.turei_process_control.time_use_to_excel_report', 'wzd.time.use.to.excel')
