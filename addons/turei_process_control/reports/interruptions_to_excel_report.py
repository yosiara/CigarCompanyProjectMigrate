# -*- coding: utf-8 -*-

import xlsxwriter
from odoo import models,fields, api, tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class InterruptionsToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        control_models = self.env['turei_process_control.tecnolog_control_model'].search([('date', '>=', lines.date_start), ('date', '<=', lines.date_end)])
        if not control_models:
            self.env.user.notify_info(tools.ustr('No existen datos que mostrar.'))
            return

        worksheet = workbook.add_worksheet("Interrupciones")
        worksheet.set_column('B:M', 22)
        worksheet.set_column('F4:F4', 25)
        worksheet.set_column('I4:I4', 25)
        worksheet.set_column('G4:G4', 25)
        worksheet.set_column('H4:H4', 25)

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
        worksheet.write('G4', tools.ustr('Línea'), merge_format)
        worksheet.write('H4', tools.ustr('Máquina'), merge_format)
        worksheet.write('I4', tools.ustr('Subconjunto'), merge_format)
        worksheet.write('J4', tools.ustr('Tipo de interrupción'), merge_format)
        worksheet.write('K4', tools.ustr('Exógena/Endógena'), merge_format)
        worksheet.write('L4', tools.ustr('Tiempo (Minutos)'), merge_format)
        worksheet.write('M4', tools.ustr('Fecuencia'), merge_format)

        aux_row = 5
        for c_model in control_models:
            date = fields.datetime.strptime(c_model.date, DEFAULT_SERVER_DATE_FORMAT)

            for interruption in c_model.interruptions:
                worksheet.write_number('B'+str(aux_row), date.year, fecha_data_format)
                worksheet.write_number('C'+str(aux_row), date.month, fecha_data_format)
                worksheet.write_number('D'+str(aux_row), date.day, fecha_data_format)
                worksheet.write('E'+str(aux_row), c_model.turn.name, data_format)
                worksheet.write('F'+str(aux_row), c_model.productive_section.name, data_format)
                if interruption.productive_line_id.productive_line.name:
                    worksheet.write('G'+str(aux_row), interruption.productive_line_id.productive_line.name, data_format)
                else:
                    worksheet.write('G'+str(aux_row), "", data_format)

                if interruption.machine_id.name:
                    worksheet.write('H'+str(aux_row), interruption.machine_id.name, data_format)
                else:
                    worksheet.write('H'+str(aux_row), "", data_format)

                if interruption.set_of_peaces_id.name:
                    worksheet.write('I'+str(aux_row), interruption.set_of_peaces_id.name, data_format)
                else:
                    worksheet.write('I'+str(aux_row), "", data_format)

                if interruption.interruption_type.name:
                    worksheet.write('J'+str(aux_row), interruption.interruption_type.name, data_format)
                else:
                    worksheet.write('J'+str(aux_row), "", data_format)

                if interruption.interruption_type.cause:
                    worksheet.write('K'+str(aux_row), interruption.interruption_type.cause, data_format)
                else:
                    worksheet.write('K'+str(aux_row), "", data_format)

                if interruption.time:
                    if interruption.interruption_type.cause == 'exogena' and not interruption.productive_line_id:
                        worksheet.write('L'+str(aux_row), interruption.time * 2, data_format)
                    elif not interruption.productive_line_id:
                        worksheet.write('L'+str(aux_row), interruption.time * 2, data_format)
                    else:
                        worksheet.write('L'+str(aux_row), interruption.time, data_format)
                else:
                    worksheet.write('L'+str(aux_row), "", data_format)

                if interruption.frequency:
                    worksheet.write('M'+str(aux_row), interruption.frequency, data_format)
                else:
                    worksheet.write('M'+str(aux_row), "", data_format)

                aux_row += 1


InterruptionsToExcelReport('report.turei_process_control.interruptions_to_excel_report', 'wzd.interruptions.to.excel')
