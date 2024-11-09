# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ResumenTimeFrequencyToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        productive_sections = self.env['process_control.productive_section'].search([('active', '=', True)], order="name")

        query = """
            SELECT DISTINCT
                process_control_interruption_type.id,
                process_control_interruption_type.name,
                process_control_interruption_type.code,
                process_control_machine_type.name as machine_type,
				process_control_interruption_type.cause,
				process_control_machine.machine_type_id
            FROM
                process_control_tecnolog_control INNER JOIN
                process_control_interruption ON process_control_tecnolog_control."id" = process_control_interruption.tec_control_model
            INNER JOIN process_control_interruption_type 
            ON process_control_interruption_type.ID = process_control_interruption.interruption_type
            LEFT JOIN process_control_machine ON process_control_interruption.machine_id = process_control_machine.id
            LEFT JOIN process_control_machine_type ON process_control_machine_type.id = process_control_machine.machine_type_id
            WHERE process_control_tecnolog_control."date" BETWEEN '%s' and '%s'
        """

        if lines.turn:
            query += """ and process_control_tecnolog_control.turn = %d
            GROUP BY process_control_interruption_type.id, cause,process_control_interruption_type.name,process_control_machine_type.name,process_control_machine.machine_type_id
            ORDER BY cause DESC, machine_type ASC """
        else:
            query += """ GROUP BY process_control_interruption_type.id,process_control_interruption_type.name,cause,process_control_machine_type.name,process_control_machine.machine_type_id
            ORDER BY cause DESC, machine_type ASC """

        worksheet = workbook.add_worksheet(tools.ustr("Tiempo"))
        worksheet.insert_textbox('A1:K1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) TURNO %d") % (lines.date_start, lines.date_end, lines.turn),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                   'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) ") % (lines.date_start, lines.date_end),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                   'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['process_control']['addons_path'] + '/process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})

        worksheet.set_column('A4:A4', 40)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Interrupción'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('B4', 'UM', merge_format)

        column_index = 2
        for ps in productive_sections:
            worksheet.write(3, column_index, 'Sp.' + ps.name[-2:], merge_format)
            column_index += 1

        if lines.turn:
            self.env.cr.execute(query % (lines.date_start, lines.date_end, lines.turn))
        else:
            self.env.cr.execute(query % (lines.date_start, lines.date_end))
        records_query = self.env.cr.dictfetchall()

        row_index = 4
        for i in range(0, len(records_query)):
            worksheet.write(row_index, 0, records_query[i]['name'] + ' ' + (records_query[i]['machine_type'] if records_query[i]['code'] in ['PM','PE','PC'] else ''),
                            workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
            worksheet.write(row_index, 1, 'Hora', workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            column_index = 2
            for ps in productive_sections:
                query_time = """
                SELECT DISTINCT
                    SUM(process_control_interruption."time")
                FROM
                    process_control_tecnolog_control INNER JOIN
                    process_control_interruption ON process_control_tecnolog_control."id" = process_control_interruption.tec_control_model
                INNER JOIN process_control_interruption_type 
                ON process_control_interruption_type.ID = process_control_interruption.interruption_type
                LEFT JOIN process_control_machine ON process_control_interruption.machine_id = process_control_machine.id
                LEFT JOIN process_control_machine_type ON process_control_machine_type.id = process_control_machine.machine_type_id
                WHERE process_control_tecnolog_control.productive_section = %d
                            and process_control_tecnolog_control."date" BETWEEN '%s' and '%s'
                            and process_control_interruption_type.id = %d 
                """

                if records_query[i]['machine_type_id']:
                    query_time += " and process_control_machine.machine_type_id = %d"
                    #query_time %= (ps.id, lines.turn , lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'])
                #else:
                    #query_time %= (ps.id, lines.turn, lines.date_start, lines.date_end, records_query[i]['id'])
                if lines.turn:
                    query_time += " and process_control_tecnolog_control.turn = %d"

                if records_query[i]['machine_type_id'] and lines.turn:
                    query_time %= (ps.id, lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'], lines.turn)

                elif records_query[i]['machine_type_id'] and not lines.turn:
                    query_time %= (ps.id, lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'])

                elif not records_query[i]['machine_type_id'] and lines.turn:
                    query_time %= (ps.id, lines.date_start, lines.date_end, records_query[i]['id'], lines.turn)

                elif not records_query[i]['machine_type_id'] and not lines.turn:
                    query_time %= (ps.id, lines.date_start, lines.date_end, records_query[i]['id'])


                self.env.cr.execute(query_time)
                records_time = self.env.cr.dictfetchall()
                if records_time[0]['sum']:
                    if records_query[i]['cause'] == 'exogena':
                        valor = records_time[0]['sum']
                    else:
                        valor = records_time[0]['sum']
                    worksheet.write_number(row_index, column_index, round(valor / 60.0, 2),
                                           workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                else:
                    worksheet.write_number(row_index, column_index, 0.00, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                column_index += 1
            row_index += 1

        worksheet = workbook.add_worksheet(tools.ustr("Frecuencia"))
        worksheet.insert_textbox('A1:K1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) TURNO %d") % (lines.date_start, lines.date_end, lines.turn),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) ") % (lines.date_start, lines.date_end),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['process_control']['addons_path'] + '/process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:A4', 40)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Interrupción'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('B4', 'UM', merge_format)

        column_index = 2
        for ps in productive_sections:
            worksheet.write(3, column_index, 'Sp.' + ps.name[-2:], merge_format)
            column_index += 1
        if lines.turn:
            self.env.cr.execute(query % (lines.date_start, lines.date_end, lines.turn))
        else:
            self.env.cr.execute(query % (lines.date_start, lines.date_end))
        records_query = self.env.cr.dictfetchall()

        row_index = 4
        for i in range(0, len(records_query)):
            worksheet.write(row_index, 0, records_query[i]['name'] + ' ' + (records_query[i]['machine_type'] if records_query[i]['machine_type'] else ''),
                            workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
            worksheet.write(row_index, 1, 'U', workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            column_index = 2
            for ps in productive_sections:
                query_time = """
                SELECT DISTINCT
                    SUM(process_control_interruption."frequency")
                FROM
                    process_control_tecnolog_control INNER JOIN
                    process_control_interruption ON process_control_tecnolog_control."id" = process_control_interruption.tec_control_model
                INNER JOIN process_control_interruption_type 
                ON process_control_interruption_type.ID = process_control_interruption.interruption_type
                LEFT JOIN process_control_machine ON process_control_interruption.machine_id = process_control_machine.id
                LEFT JOIN process_control_machine_type ON process_control_machine_type.id = process_control_machine.machine_type_id
                WHERE process_control_tecnolog_control.productive_section = %d
                            and process_control_tecnolog_control."date" BETWEEN '%s' and '%s'
                            and process_control_interruption_type.id = %d
                """

                if records_query[i]['machine_type_id']:
                    query_time += " and process_control_machine.machine_type_id = %d"
                    #query_time %= (ps.id, lines.turn , lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'])
                #else:
                    #query_time %= (ps.id, lines.turn, lines.date_start, lines.date_end, records_query[i]['id'])
                if lines.turn:
                    query_time += " and process_control_tecnolog_control.turn = %d"

                if records_query[i]['machine_type_id'] and lines.turn:
                    query_time %= (ps.id, lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'], lines.turn)

                elif records_query[i]['machine_type_id'] and not lines.turn:
                    query_time %= (ps.id, lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'])

                elif not records_query[i]['machine_type_id'] and lines.turn:
                    query_time %= (ps.id, lines.date_start, lines.date_end, records_query[i]['id'], lines.turn)

                elif not records_query[i]['machine_type_id'] and not lines.turn:
                    query_time %= (ps.id, lines.date_start, lines.date_end, records_query[i]['id'])

                self.env.cr.execute(query_time)
                records_time = self.env.cr.dictfetchall()
                if records_time[0]['sum']:
                    worksheet.write_number(row_index, column_index, records_time[0]['sum'],
                                           workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                else:
                    worksheet.write_number(row_index, column_index, 0.00, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                column_index += 1
            row_index += 1


ResumenTimeFrequencyToExcelReport('report.process_control.resume_time_frequency_report', 'wzd.resume.time.frequency.excel')


class ResumenTimeFrequencybyLinesToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        productive_lines = self.env['process_control.productive_section_lines'].search([], order="productive_line")

        query = """
            SELECT DISTINCT
                process_control_interruption_type.id,
                process_control_interruption_type.name,
                process_control_machine_type.name as machine_type,
				process_control_interruption_type.cause,
				process_control_machine.machine_type_id
            FROM
                process_control_tecnolog_control INNER JOIN
                process_control_interruption ON process_control_tecnolog_control."id" = process_control_interruption.tec_control_model
            INNER JOIN process_control_interruption_type 
            ON process_control_interruption_type.ID = process_control_interruption.interruption_type
            LEFT JOIN process_control_machine ON process_control_interruption.machine_id = process_control_machine.id
            LEFT JOIN process_control_machine_type ON process_control_machine_type.id = process_control_machine.machine_type_id
            WHERE process_control_tecnolog_control."date" BETWEEN '%s' and '%s'
        """

        worksheet = workbook.add_worksheet(tools.ustr("Tiempo"))
        worksheet.insert_textbox('A1:K1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) TURNO %d") % (lines.date_start, lines.date_end, lines.turn),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) ") % (lines.date_start, lines.date_end),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['process_control']['addons_path'] + '/process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:A4', 40)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Interrupción'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('B4', 'UM', merge_format)

        column_index = 2
        for ln in productive_lines:
            worksheet.write(3, column_index, 'ln.' + ln.productive_line.name[-2:], merge_format)
            column_index += 1

        if lines.turn:
            query += """ and process_control_tecnolog_control.turn = %d
            GROUP BY process_control_interruption_type.id, cause,process_control_interruption_type.name,process_control_machine_type.name,process_control_machine.machine_type_id
            ORDER BY cause DESC, machine_type ASC """
            self.env.cr.execute(query % (lines.date_start, lines.date_end, lines.turn))
        else:
            query += """ GROUP BY process_control_interruption_type.id, cause,process_control_interruption_type.name,process_control_machine_type.name,process_control_machine.machine_type_id
            ORDER BY cause DESC, machine_type ASC """
            self.env.cr.execute(query % (lines.date_start, lines.date_end))

        records_query = self.env.cr.dictfetchall()

        row_index = 4
        for i in range(0, len(records_query)):
            worksheet.write(row_index, 0, records_query[i]['name'] + ' ' + (records_query[i]['machine_type'] if records_query[i]['machine_type'] else ''),
                            workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
            worksheet.write(row_index, 1, 'Hora', workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            column_index = 2
            for ln in productive_lines:
                query_time = """
                SELECT DISTINCT
                    SUM(process_control_interruption."time")
                FROM
                    process_control_tecnolog_control INNER JOIN
                    process_control_interruption ON process_control_tecnolog_control."id" = process_control_interruption.tec_control_model
                INNER JOIN process_control_interruption_type 
                ON process_control_interruption_type.ID = process_control_interruption.interruption_type
                LEFT JOIN process_control_machine ON process_control_interruption.machine_id = process_control_machine.id
                LEFT JOIN process_control_machine_type ON process_control_machine_type.id = process_control_machine.machine_type_id
                WHERE process_control_interruption.productive_line_id = %d
                            and process_control_tecnolog_control."date" BETWEEN '%s' and '%s'
                            and process_control_interruption_type.id = %d 
                """

                if records_query[i]['machine_type_id']:
                    query_time += " and process_control_machine.machine_type_id = %d"
                if lines.turn:
                    query_time += " and process_control_tecnolog_control.turn = %d"

                if records_query[i]['machine_type_id'] and lines.turn:
                    query_time %= (ln.id, lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'], lines.turn)

                elif records_query[i]['machine_type_id'] and not lines.turn:
                    query_time %= (ln.id, lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'])

                elif not records_query[i]['machine_type_id'] and lines.turn:
                    query_time %= (ln.id, lines.date_start, lines.date_end, records_query[i]['id'], lines.turn)

                elif not records_query[i]['machine_type_id'] and not lines.turn:
                    query_time %= (ln.id, lines.date_start, lines.date_end, records_query[i]['id'])

                self.env.cr.execute(query_time)
                records_time = self.env.cr.dictfetchall()
                if records_time[0]['sum']:
                    worksheet.write_number(row_index, column_index, round(records_time[0]['sum'] / 60.0, 2),
                                           workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                else:
                    worksheet.write_number(row_index, column_index, 0.00, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                column_index += 1
            row_index += 1

        worksheet = workbook.add_worksheet(tools.ustr("Frecuencia"))
        worksheet.insert_textbox('A1:K1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) TURNO %d") % (lines.date_start, lines.date_end, lines.turn),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) ") % (lines.date_start, lines.date_end),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['process_control']['addons_path'] + '/process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:A4', 40)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Interrupción'), merge_format)
        worksheet.write('B4', 'UM', workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))

        column_index = 2
        for ln in productive_lines:
            worksheet.write(3, column_index, 'ln.' + ln.productive_line.name[-2:], workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            column_index += 1

        if lines.turn:
            self.env.cr.execute(query % (lines.date_start, lines.date_end, lines.turn))
        else:
            self.env.cr.execute(query % (lines.date_start, lines.date_end))
        records_query = self.env.cr.dictfetchall()

        row_index = 4
        for i in range(0, len(records_query)):
            worksheet.write(row_index, 0, records_query[i]['name'] + ' ' + (records_query[i]['machine_type'] if records_query[i]['machine_type'] else ''),
                            workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
            worksheet.write(row_index, 1, 'U', workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            column_index = 2
            for ln in productive_lines:
                query_time = """
                SELECT DISTINCT
                    SUM(process_control_interruption."frequency")
                FROM
                    process_control_tecnolog_control INNER JOIN
                    process_control_interruption ON process_control_tecnolog_control."id" = process_control_interruption.tec_control_model
                INNER JOIN process_control_interruption_type 
                ON process_control_interruption_type.ID = process_control_interruption.interruption_type
                LEFT JOIN process_control_machine ON process_control_interruption.machine_id = process_control_machine.id
                LEFT JOIN process_control_machine_type ON process_control_machine_type.id = process_control_machine.machine_type_id
                WHERE process_control_interruption.productive_line_id = %d
                            and process_control_tecnolog_control."date" BETWEEN '%s' and '%s'
                            and process_control_interruption_type.id = %d
                """

                if records_query[i]['machine_type_id']:
                    query_time += " and process_control_machine.machine_type_id = %d"
                if lines.turn:
                    query_time += " and process_control_tecnolog_control.turn = %d"

                if records_query[i]['machine_type_id'] and lines.turn:
                    query_time %= (ln.id, lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'], lines.turn)

                elif records_query[i]['machine_type_id'] and not lines.turn:
                    query_time %= (ln.id, lines.date_start, lines.date_end, records_query[i]['id'], records_query[i]['machine_type_id'])

                elif not records_query[i]['machine_type_id'] and lines.turn:
                    query_time %= (ln.id, lines.date_start, lines.date_end, records_query[i]['id'], lines.turn)

                elif not records_query[i]['machine_type_id'] and not lines.turn:
                    query_time %= (ln.id, lines.date_start, lines.date_end, records_query[i]['id'])

                self.env.cr.execute(query_time)
                records_time = self.env.cr.dictfetchall()
                if records_time[0]['sum']:
                    worksheet.write_number(row_index, column_index, records_time[0]['sum'],
                                           workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                else:
                    worksheet.write_number(row_index, column_index, 0.00, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                column_index += 1
            row_index += 1


ResumenTimeFrequencybyLinesToExcelReport('report.process_control.resume_time_frequency_by_line_report', 'wzd.resume.time.frequency.excel')
