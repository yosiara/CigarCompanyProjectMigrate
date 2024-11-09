# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class EfficiencyCdtExcelReport(ReportXlsx):
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
                                                         'productividad_real': 0.00,
                                                         'productividad_operativa': 0.00,
                                                         'count': count,
                                                         'count_lines': len(
                                                             self.env['turei_process_control.productive_section'].search([('id', '=', records_query[i]['productive_section'])]).productive_line_ids)
                                                         })
                if not records_query[i]['productive_line']:
                    records[records_query[i]['key']]['total_time'] = records[records_query[i]['key']]['total_time'] * records[records_query[i]['key']]['count_lines']
                    if records_query[i]['cause'] == 'endogena':
                        records[records_query[i]['key']]['endogena'] = records[records_query[i]['key']]['endogena'] * records[records_query[i]['key']]['count_lines']
                    if records_query[i]['cause'] == 'exogena':
                        records[records_query[i]['key']]['exogena'] = records[records_query[i]['key']]['exogena'] * records[records_query[i]['key']]['count_lines']

                records[records_query[i]['key']]['productividad_real'] = (records_query[i]['plan_time'] * 60.0) * records_query[i]['productive_capacity']

                records[records_query[i]['key']]['productividad_operativa'] = ((records_query[i]['plan_time'] * 60.0) - records[records_query[i]['key']]['exogena']) * records_query[i]['productive_capacity']

                key_last = records_query[i]['key']
            else:
                count += 1
                records[records_query[i]['key']]['total_frequency'] += records_query[i]['total_frequency']

                if not records_query[i]['productive_line']:
                    records[records_query[i]['key']]['total_time'] += records_query[i]['total_time'] * records[records_query[i]['key']]['count_lines']
                    if records_query[i]['cause'] == 'endogena':
                        records[records_query[i]['key']]['endogena'] += records_query[i]['total_time'] * records[records_query[i]['key']]['count_lines']
                    if records_query[i]['cause'] == 'exogena':
                        records[records_query[i]['key']]['exogena'] += records_query[i]['total_time'] * records[records_query[i]['key']]['count_lines']
                else:
                    records[records_query[i]['key']]['total_time'] += records_query[i]['total_time']
                    records[records_query[i]['key']]['endogena'] += records_query[i]['total_time'] if records_query[i]['cause'] == 'endogena' else 0.00
                    records[records_query[i]['key']]['exogena'] += records_query[i]['total_time'] if records_query[i]['cause'] == 'exogena' else 0.00
                records[records_query[i]['key']]['count'] = count

                records[records_query[i]['key']]['productividad_operativa'] = ((records_query[i]['plan_time'] * 60.0) - records[records_query[i]['key']]['exogena']) * records_query[i]['productive_capacity']

        worksheet = workbook.add_worksheet(tools.ustr("Eficiencia y CDT"))
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
        worksheet.write('F4', tools.ustr('Modulo'), merge_format)
        worksheet.write('G4', tools.ustr('Eficiencia Real'), merge_format)
        worksheet.write('H4', tools.ustr('Eficiencia Operativa'), merge_format)
        worksheet.write('I4', tools.ustr('Coeficiente de Disponibilidad Técnica Real'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 25}}))
        worksheet.write('J4', tools.ustr('Coeficiente de Disponibilidad Técnica Operativo'),
                        workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 25}}))

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

            # Producción realizada*10000 / (Tiempo Total Planificado) * Capacidad productiva) * 100
            real_efficiency = round((c_model[1].get('production_done') * 10000.0 / c_model[1].get('productividad_real')) * 100.00, 2)
            worksheet.write('G' + str(aux_row), real_efficiency, data_format)

            try:
                real_efficiency_opr = round((c_model[1].get('production_done') * 10000.0 / c_model[1].get('productividad_operativa')) * 100.00, 2)
                worksheet.write('H' + str(aux_row), real_efficiency_opr, data_format)
            except ZeroDivisionError:
                worksheet.write('H' + str(aux_row), 0.00, data_format)

            cdt = round((((60.00 * c_model[1].get('plan_time')) - ((c_model[1].get('exogena') + c_model[1].get('endogena')) / c_model[1].get('count_lines'))) / (60.00 * c_model[1].get('plan_time'))) * 100.00,
                        2)
            worksheet.write('I' + str(aux_row), cdt, data_format)

            cdt_o = round(((60.00 * c_model[1].get('plan_time') - (c_model[1].get('endogena') / c_model[1].get('count_lines'))) / (60.00 * c_model[1].get('plan_time'))) * 100.00, 2)
            worksheet.write('J' + str(aux_row), cdt_o, data_format)


EfficiencyCdtExcelReport('report.turei_process_control.efficiency_cdt_excel_report', 'wzd.efficiency.cdt.excel')
