# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ResumenTimeFrequencynToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        productive_sections = self.env['turei_process_control.productive_section'].search([('active', '=', True)], order="name")

        worksheet = workbook.add_worksheet(tools.ustr("Tiempo"))
        worksheet.insert_textbox('A1:K1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            # self.env['resource.calendar'].browse([lines.turn]).sgp_turn_id.sgp_id
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) TURNO %d") % (lines.date_start, lines.date_end, lines.turn.sgp_turn_id.sgp_id),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                   'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) ") % (lines.date_start, lines.date_end),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                   'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})

        worksheet.set_column('A4:A4', 40)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        normal_format1 = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 11}})
        worksheet.write('A4', tools.ustr('Interrupción'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('B4', 'UM', merge_format)

        column_index = 2
        for ps in productive_sections:
            worksheet.write(3, column_index, 'Sp.' + ps.name[-2:], merge_format)
            column_index += 1

        if lines.turn:
            tecnolog_control = self.env['turei_process_control.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('turn', '=', lines.turn.id)])
        else:
            tecnolog_control = self.env['turei_process_control.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)])

        dic_int, dic_int_fr = {}, {}
        for tc in tecnolog_control:
            for it in tc.interruptions:
                if it.interruption_type.cause == 'exogena':
                    if not it.interruption_type.code in dic_int_fr:
                        dic_fr2 = {}
                        for d in productive_sections:
                            dic_fr2.setdefault(int(d.name[-2:]), 0)
                        dic_int_fr.setdefault(it.interruption_type.code, dic_fr2)
                        dic_int_fr[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.frequency
                    else:
                        dic_int_fr[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.frequency  + dic_int_fr[it.interruption_type.code][int(tc.productive_section.name[-2:])]

                    if not it.interruption_type.code in dic_int:
                        dic_sp2 = {}
                        for d in productive_sections:
                            dic_sp2.setdefault(int(d.name[-2:]), 0.0)
                        dic_int.setdefault(it.interruption_type.code, dic_sp2)
                        if not it.productive_line_id:
                            dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.time * len(tc.productive_section.productive_line_ids)
                        else:
                            dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.time
                    else:
                        if not it.productive_line_id:
                            dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])] = (it.time * len(tc.productive_section.productive_line_ids)) + dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])]
                        else:
                            dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])] = (it.time ) + dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])]
                else:
                    if it.interruption_type.code in ['PM','PE','PC']:
                        valor = str(it.interruption_type.code) + " " + str(it.machine_id.machine_type_id.name)

                        if not valor in dic_int_fr:
                            dic_fr = {}
                            for d in productive_sections:
                                dic_fr.setdefault(int(d.name[-2:]),0.0)
                            dic_int_fr.setdefault(valor,dic_fr)
                            dic_int_fr[valor][int(tc.productive_section.name[-2:])] = it.frequency
                        else:
                            dic_int_fr[valor][int(tc.productive_section.name[-2:])] = it.frequency + dic_int_fr[valor][int(tc.productive_section.name[-2:])]

                        if not valor in dic_int:
                            dic_sp = {}
                            for d in productive_sections:
                                dic_sp.setdefault(int(d.name[-2:]),0)
                            dic_int.setdefault(valor,dic_sp)
                            if not it.productive_line_id:
                                dic_int[valor][int(tc.productive_section.name[-2:])] = it.time * len(tc.productive_section.productive_line_ids)
                            else:
                                dic_int[valor][int(tc.productive_section.name[-2:])] = it.time
                        else:
                            if not it.productive_line_id:
                                dic_int[valor][int(tc.productive_section.name[-2:])] = (it.time * len(tc.productive_section.productive_line_ids)) + dic_int[valor][int(tc.productive_section.name[-2:])]
                            else:
                                dic_int[valor][int(tc.productive_section.name[-2:])] = it.time + dic_int[valor][int(tc.productive_section.name[-2:])]

                    else:
                        if not it.interruption_type.code in dic_int_fr:
                            dic_fr1 = {}
                            for d in productive_sections:
                                dic_fr1.setdefault(int(d.name[-2:]),0)
                            dic_int_fr.setdefault(it.interruption_type.code,dic_fr1)
                            dic_int_fr[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.frequency
                        else:
                            dic_int_fr[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.frequency + dic_int_fr[it.interruption_type.code][int(tc.productive_section.name[-2:])]

                        if not it.interruption_type.code in dic_int:
                            dic_sp1 = {}
                            for d in productive_sections:
                                dic_sp1.setdefault(int(d.name[-2:]),0.0)
                            dic_int.setdefault(it.interruption_type.code,dic_sp1)
                            if not it.productive_line_id:
                                dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.time * len(tc.productive_section.productive_line_ids)
                            else:
                                dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.time
                        else:
                            if not it.productive_line_id:
                                dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])] = (it.time * len(tc.productive_section.productive_line_ids)) + dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])]
                            else:
                                dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])] = it.time + dic_int[it.interruption_type.code][int(tc.productive_section.name[-2:])]

        fila_index = 4
        for i in dic_int.items():
            worksheet.write(fila_index, 0, i[0], normal_format)
            worksheet.write(fila_index, 1, tools.ustr('Hora'), normal_format1)
            column_index = 2
            for a in productive_sections:
                worksheet.write(fila_index, column_index, round(float(i[1][int(a.name[-2:])]) / 60 /len(a.productive_line_ids),2) , normal_format1)
                column_index += 1
            fila_index += 1

        worksheet = workbook.add_worksheet(tools.ustr("Frecuencia"))
        worksheet.insert_textbox('A1:K1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) TURNO %d") % (lines.date_start, lines.date_end, lines.turn.sgp_turn_id.sgp_id),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) ") % (lines.date_start, lines.date_end),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:A4', 40)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Interrupción'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('B4', 'UM', merge_format)

        column_index = 2
        for ps in productive_sections:
            worksheet.write(3, column_index, 'Sp.' + ps.name[-2:], merge_format)
            column_index += 1

        fila_index = 4
        for i in dic_int_fr.items():
            worksheet.write(fila_index, 0, i[0], normal_format)
            worksheet.write(fila_index, 1, tools.ustr('UM'), normal_format1)
            column_index = 2
            for a in productive_sections:
                worksheet.write(fila_index, column_index, i[1][int(a.name[-2:])] , normal_format1)
                column_index += 1
            fila_index += 1




ResumenTimeFrequencynToExcelReport('report.turei_process_control.resume_time_frequencyn_report', 'wzd.resume.time.frequencyn.excel')


class ResumenTimeFrequencynbyLinesToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        productive_lines = self.env['turei_process_control.productive_section_lines'].search([], order="productive_line")
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        normal_format1 = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 11}})

        worksheet = workbook.add_worksheet(tools.ustr("Tiempo"))
        worksheet.insert_textbox('A1:K1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) TURNO %d") % (lines.date_start, lines.date_end, lines.turn.sgp_turn_id.sgp_id),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) ") % (lines.date_start, lines.date_end),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:A4', 40)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Interrupción'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('B4', 'UM', merge_format)

        column_index = 2
        for ln in productive_lines:
            worksheet.write(3, column_index, 'ln.' + ln.productive_line.name[-2:], merge_format)
            column_index += 1

        if lines.turn:
            tecnolog_control = self.env['turei_process_control.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('turn', '=', lines.turn.id)])
        else:
            tecnolog_control = self.env['turei_process_control.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)])

        dic_int, dic_int_fr = {}, {}
        for tc in tecnolog_control:
            for it in tc.interruptions:

                if it.interruption_type.cause == 'exogena':
                    if not it.interruption_type.code in dic_int_fr:
                        dic_fr2 = {}
                        for d in productive_lines:
                            dic_fr2.setdefault(int(d.productive_line.name[-2:]), 0)
                        dic_int_fr.setdefault(it.interruption_type.code, dic_fr2)
                        for ln in tc.productive_section.productive_line_ids:
                            dic_int_fr[it.interruption_type.code][int(ln.productive_line.name[-2:])] = it.frequency
                    else:
                        for ln in tc.productive_section.productive_line_ids:
                            dic_int_fr[it.interruption_type.code][int(ln.productive_line.name[-2:])] = it.frequency  + dic_int_fr[it.interruption_type.code][int(ln.productive_line.name[-2:])]

                    if not it.interruption_type.code in dic_int:
                        dic_sp2 = {}
                        for d in productive_lines:
                            dic_sp2.setdefault(int(d.productive_line.name[-2:]), 0.00)
                        dic_int.setdefault(it.interruption_type.code, dic_sp2)
                        for ln in tc.productive_section.productive_line_ids:
                            dic_int[it.interruption_type.code][int(ln.productive_line.name[-2:])] = it.time
                    else:
                        for ln in tc.productive_section.productive_line_ids:
                            dic_int[it.interruption_type.code][int(ln.productive_line.name[-2:])] = it.time + dic_int[it.interruption_type.code][int(ln.productive_line.name[-2:])]
                else:
                    if it.interruption_type.code in ['PM','PE','PC']:
                        valor = str(it.interruption_type.code) + " " + str(it.machine_id.machine_type_id.name)

                        if not valor in dic_int_fr:
                            dic_fr = {}
                            for d in productive_lines:
                                dic_fr.setdefault(int(d.productive_line.name[-2:]),0)
                            dic_int_fr.setdefault(valor,dic_fr)
                            if it.productive_line_id.productive_line:
                                dic_int_fr[valor][int(it.productive_line_id.productive_line.name[-2:])] = it.frequency
                            else:
                                for ln in tc.productive_section.productive_line_ids:
                                    dic_int_fr[valor][int(ln.productive_line.name[-2:])] = it.frequency
                        else:
                            if it.productive_line_id.productive_line:
                                dic_int_fr[valor][int(it.productive_line_id.productive_line.name[-2:])] = it.frequency + dic_int_fr[valor][int(it.productive_line_id.productive_line.name[-2:])]
                            else:
                                for ln in tc.productive_section.productive_line_ids:
                                    dic_int_fr[valor][int(ln.productive_line.name[-2:])] = it.frequency + dic_int_fr[valor][int(ln.productive_line.name[-2:])]

                        if not valor in dic_int:
                            dic_sp = {}
                            for d in productive_lines:
                                dic_sp.setdefault(int(d.productive_line.name[-2:]),0.00)
                            dic_int.setdefault(valor,dic_sp)
                            if it.productive_line_id.productive_line:
                                dic_int[valor][int(it.productive_line_id.productive_line.name[-2:])] = it.time
                            else:
                                for ln in tc.productive_section.productive_line_ids:
                                    dic_int[valor][int(ln.productive_line.name[-2:])] = it.time
                        else:
                            if it.productive_line_id.productive_line:
                                dic_int[valor][int(it.productive_line_id.productive_line.name[-2:])] = it.time + dic_int[valor][int(it.productive_line_id.productive_line.name[-2:])]
                            else:
                                for ln in tc.productive_section.productive_line_ids:
                                    dic_int[valor][int(ln.productive_line.name[-2:])] = it.time + dic_int[valor][int(ln.productive_line.name[-2:])]

                    else:
                        if not it.interruption_type.code in dic_int_fr:
                            dic_fr1 = {}
                            for d in productive_lines:
                                dic_fr1.setdefault(int(d.productive_line.name[-2:]),0)
                            dic_int_fr.setdefault(it.interruption_type.code,dic_fr1)
                            if it.productive_line_id.productive_line:
                                dic_int_fr[it.interruption_type.code][int(it.productive_line_id.productive_line.name[-2:])] = it.frequency
                            else:
                                for ln in tc.productive_section.productive_line_ids:
                                    dic_int_fr[it.interruption_type.code][int(ln.productive_line.name[-2:])] = it.frequency
                        else:
                            if it.productive_line_id.productive_line:
                                dic_int_fr[it.interruption_type.code][int(it.productive_line_id.productive_line.name[-2:])] = it.frequency + dic_int_fr[it.interruption_type.code][int(it.productive_line_id.productive_line.name[-2:])]
                            else:
                                for ln in tc.productive_section.productive_line_ids:
                                    dic_int_fr[it.interruption_type.code][int(ln.productive_line.name[-2:])] = it.frequency + dic_int_fr[it.interruption_type.code][int(ln.productive_line.name[-2:])]

                        if not it.interruption_type.code in dic_int:
                            dic_sp1 = {}
                            for d in productive_lines:
                                dic_sp1.setdefault(int(d.productive_line.name[-2:]),0.00)
                            dic_int.setdefault(it.interruption_type.code,dic_sp1)
                            if it.productive_line_id.productive_line:
                                dic_int[it.interruption_type.code][int(it.productive_line_id.productive_line.name[-2:])] = it.time
                            else:
                                for ln in tc.productive_section.productive_line_ids:
                                    dic_int[it.interruption_type.code][int(ln.productive_line.name[-2:])] = it.time
                        else:
                            if it.productive_line_id.productive_line:
                                dic_int[it.interruption_type.code][int(it.productive_line_id.productive_line.name[-2:])] = it.time + dic_int[it.interruption_type.code][int(it.productive_line_id.productive_line.name[-2:])]
                            else:
                                for ln in tc.productive_section.productive_line_ids:
                                    dic_int[it.interruption_type.code][int(ln.productive_line.name[-2:])] = it.time + dic_int[it.interruption_type.code][int(ln.productive_line.name[-2:])]

        fila_index = 4
        for i in dic_int.items():
            worksheet.write(fila_index, 0, i[0], normal_format)
            worksheet.write(fila_index, 1, tools.ustr('Hora'), normal_format1)
            column_index = 2
            for a in productive_lines:
                worksheet.write(fila_index, column_index, round(float(i[1][int(a.productive_line.name[-2:])]) / 60 /len(a.productive_section_id.productive_line_ids),2) , normal_format1)
                column_index += 1
            fila_index += 1

        worksheet = workbook.add_worksheet(tools.ustr("Frecuencia"))
        worksheet.insert_textbox('A1:K1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) TURNO %d") % (lines.date_start, lines.date_end, lines.turn.sgp_turn_id.sgp_id),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:K2', tools.ustr("REPORTE RESUMEN DE TIEMPO Y FRECUENCIA POR Modulo (DESDE %s HASTA %s) ") % (lines.date_start, lines.date_end),
                             options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                              'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                      'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:A4', 40)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Interrupción'), merge_format)
        worksheet.write('B4', 'UM', workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))

        column_index = 2
        for ln in productive_lines:
            worksheet.write(3, column_index, 'ln.' + ln.productive_line.name[-2:], merge_format)
            column_index += 1

        fila_index = 4
        for i in dic_int_fr.items():
            worksheet.write(fila_index, 0, i[0], normal_format)
            worksheet.write(fila_index, 1, tools.ustr('UM'), normal_format1)
            column_index = 2
            for a in productive_lines:
                worksheet.write(fila_index, column_index, i[1][int(a.name[-2:])] , normal_format1)
                column_index += 1
            fila_index += 1

ResumenTimeFrequencynbyLinesToExcelReport('report.turei_process_control.resume_time_frequencyn_by_line_report', 'wzd.resume.time.frequencyn.excel')
