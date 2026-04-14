# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class MachineSetOfPeacesToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        productive_sections = self.env['turei_process_control.productive_section'].search([('active', '=', True)], order="name")
        machine = self.env['turei_process_control.machine_set_of_peaces_nomenclature'].search([], order="machine_type_id")

        worksheet = workbook.add_worksheet(tools.ustr("Tiempo"))
        worksheet1 = workbook.add_worksheet(tools.ustr("Frecuencia"))
        worksheet.insert_textbox('A1:M1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        worksheet1.insert_textbox('A1:M1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:M2', tools.ustr("REPORTE RESUMEN SUBCONJUNTO DE TIEMPO Y FRECUENCIA POR SECCIÓN PRODUCTIVA (DESDE %s HASTA %s) TURNO: %s") % (lines.date_start, lines.date_end, lines.turn.name[-1:]),
                                     options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                       'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                              'line': {'none': True}})
            worksheet1.insert_textbox('A2:M2', tools.ustr("REPORTE RESUMEN SUBCONJUNTO DE TIEMPO Y FRECUENCIA POR SECCIÓN PRODUCTIVA (DESDE %s HASTA %s) TURNO: %s") % (lines.date_start, lines.date_end, lines.turn.name[-1:]),
                                     options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                       'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                              'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:M2', tools.ustr("REPORTE RESUMEN SUBCONJUNTO DE TIEMPO Y FRECUENCIA POR SECCIÓN PRODUCTIVA (DESDE %s HASTA %s)") % (lines.date_start, lines.date_end),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                   'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})
            worksheet1.insert_textbox('A2:M2', tools.ustr("REPORTE RESUMEN SUBCONJUNTO DE TIEMPO Y FRECUENCIA POR SECCIÓN PRODUCTIVA (DESDE %s HASTA %s)") % (lines.date_start, lines.date_end),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                   'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})

        worksheet.insert_image('L1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet1.insert_image('L1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:A4', 20)
        worksheet1.set_column('A4:A4', 20)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Maquina'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet1.write('A4', tools.ustr('Maquina'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.set_column('B4:B4', 40)
        worksheet1.set_column('B4:B4', 40)
        worksheet.write('B4', 'SubConjunto', merge_format)
        worksheet1.write('B4', 'SubConjunto', merge_format)
        worksheet.write('C4', 'UM', merge_format)
        worksheet1.write('C4', 'UM', merge_format)

        column_index = 3
        for ps in productive_sections:
            worksheet.write(3, column_index, 'Sp.' + ps.name[-2:], merge_format)
            worksheet1.write(3, column_index, 'Sp.' + ps.name[-2:], merge_format)
            column_index += 1

        x = 4
        for m in machine:
            if m.machine_type_id.name:
                worksheet.write(x,0, m.machine_type_id.name,normal_format)
                worksheet1.write(x,0, m.machine_type_id.name,normal_format)
                worksheet.write(x,1,m.name,normal_format)
                worksheet1.write(x,1,m.name,normal_format)
                worksheet.write(x,2,'Hora',normal_format)
                worksheet1.write(x,2,'U',normal_format)
                column_index = 3
                for ps in productive_sections:
                    if lines.turn:
                        lis = self.env["turei_process_control.tecnolog_control_model"].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('productive_section','=',ps.id),('turn','=',lines.turn.id)])
                    else:
                        lis = self.env["turei_process_control.tecnolog_control_model"].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('productive_section','=',ps.id)])
                    valor = 0.0
                    frecuencia = 0
                    for a in lis:
                        for b in a.interruptions:
                           if b.set_of_peaces_id.name and b.set_of_peaces_id.name == m.name and b.machine_id.machine_type_id.name == m.machine_type_id.name:
                               valor += b.time
                               frecuencia += b.frequency

                    worksheet.write(x,column_index,round(valor / 60.0, 2),normal_format)
                    worksheet1.write(x,column_index,frecuencia,normal_format)
                    column_index += 1
                x += 1

MachineSetOfPeacesToExcelReport('report.turei_process_control.machine_set_of_peaces_report', 'wzd.machine.set.of.peaces.to.excel')

class MachineSetOfPeacesByLineToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        productive_lines = self.env['turei_process_control.productive_section_lines'].search([], order="productive_line")
        machine = self.env['turei_process_control.machine_set_of_peaces_nomenclature'].search([], order="machine_type_id")

        worksheet = workbook.add_worksheet(tools.ustr("Tiempo"))
        worksheet1 = workbook.add_worksheet(tools.ustr("Frecuencia"))
        worksheet.insert_textbox('A1:M1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        worksheet1.insert_textbox('A1:M1', tools.ustr('EMPRESA DE CIGARRO LAZARO PEÑA'), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 495, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        if lines.turn:
            worksheet.insert_textbox('A2:M2', tools.ustr("REPORTE RESUMEN SUBCONJUNTO DE TIEMPO Y FRECUENCIA POR SECCIÓN PRODUCTIVA (DESDE %s HASTA %s) TURNO: %s") % (lines.date_start, lines.date_end, lines.turn.name[-1:]),
                                     options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                       'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                              'line': {'none': True}})
            worksheet1.insert_textbox('A2:M2', tools.ustr("REPORTE RESUMEN SUBCONJUNTO DE TIEMPO Y FRECUENCIA POR SECCIÓN PRODUCTIVA (DESDE %s HASTA %s) TURNO: %s") % (lines.date_start, lines.date_end, lines.turn.name[-1:]),
                                     options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                       'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                              'line': {'none': True}})
        else:
            worksheet.insert_textbox('A2:M2', tools.ustr("REPORTE RESUMEN SUBCONJUNTO DE TIEMPO Y FRECUENCIA POR SECCIÓN PRODUCTIVA (DESDE %s HASTA %s)") % (lines.date_start, lines.date_end),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                   'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})
            worksheet1.insert_textbox('A2:M2', tools.ustr("REPORTE RESUMEN SUBCONJUNTO DE TIEMPO Y FRECUENCIA POR SECCIÓN PRODUCTIVA (DESDE %s HASTA %s)") % (lines.date_start, lines.date_end),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                   'size': 10}, 'width': 720, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})

        worksheet.insert_image('L1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet1.insert_image('L1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:A4', 20)
        worksheet1.set_column('A4:A4', 20)
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}})
        worksheet.write('A4', tools.ustr('Maquina'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet1.write('A4', tools.ustr('Maquina'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.set_column('B4:B4', 40)
        worksheet1.set_column('B4:B4', 40)
        worksheet.write('B4', 'SubConjunto', merge_format)
        worksheet1.write('B4', 'SubConjunto', merge_format)
        worksheet.write('C4', 'UM', merge_format)
        worksheet1.write('C4', 'UM', merge_format)

        column_index = 3
        for ln in productive_lines:
            worksheet.write(3, column_index, 'ln.' + ln.productive_line.name[-2:], merge_format)
            worksheet1.write(3, column_index, 'ln.' + ln.productive_line.name[-2:], merge_format)
            column_index += 1

        x = 4
        for m in machine:
            if m.machine_type_id.name:
                worksheet.write(x,0, m.machine_type_id.name,normal_format)
                worksheet1.write(x,0, m.machine_type_id.name,normal_format)
                worksheet.write(x,1,m.name,normal_format)
                worksheet1.write(x,1,m.name,normal_format)
                worksheet.write(x,2,'Hora',normal_format)
                worksheet1.write(x,2,'U',normal_format)
                column_index = 3
                for ps in productive_lines:
                    if lines.turn:
                        lis = self.env["turei_process_control.tecnolog_control_model"].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('productive_section','=',ps.productive_section_id.id),('turn','=',lines.turn.id)])
                    else:
                        lis = self.env["turei_process_control.tecnolog_control_model"].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('productive_section','=',ps.productive_section_id.id)])

                    valor = 0.0
                    frecuencia = 0
                    for a in lis:
                        for b in a.interruptions:
                            if ps.productive_line.name == b.productive_line_id.productive_line.name:
                               if b.set_of_peaces_id.name and b.set_of_peaces_id.name == m.name and b.machine_id.machine_type_id.name == m.machine_type_id.name:
                                   valor += b.time
                                   frecuencia += b.frequency

                    worksheet.write(x,column_index,round(valor / 60.0, 2),normal_format)
                    worksheet1.write(x,column_index,frecuencia,normal_format)
                    column_index += 1
                x += 1

MachineSetOfPeacesByLineToExcelReport('report.turei_process_control.machine_set_of_peaces_by_line_report', 'wzd.machine.set.of.peaces.to.excel')

