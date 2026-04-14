# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class BehaviorPreventionPlan(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet(tools.ustr('R3'))
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11})
        merge_format.set_text_wrap()
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 11})
        normal_format.set_text_wrap()
        normal_format_no_border = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vcenter', 'font_size': 11})
        normal_format_no_border.set_text_wrap()
        normal_center_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11})
        normal_center_format.set_text_wrap()
        sign_format = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vdistributed', 'font_size': 10})
        sign_format.set_text_wrap()
        sign_format.set_indent(4)
        identification_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})
        worksheet.insert_image('A1', addons_manifest['hr_turei'][
            'addons_path'] + '/enterprise_mgm_sys/static/src/img/logo-landscape.jpg',
                               {'x_offset': 15, 'y_offset': 2, 'x_scale': 1.2, 'y_scale': 1.5})
        worksheet.merge_range('C1:F3', tools.ustr('Comportamiento de los elementos del Plan de Prevención de Riesgos; Objetivos (R-3)'), merge_format)
        worksheet.merge_range('A1:B3', tools.ustr(''), merge_format)
        worksheet.merge_range('G1:J1', tools.ustr('Versión: 00'), identification_format)
        worksheet.merge_range('G2:J2', tools.ustr('Fecha de aprobación: 21/6/2018'), identification_format)
        worksheet.merge_range('G3:J3', tools.ustr('Código: M-DTD-03-R17'), identification_format)
        worksheet.merge_range('A6:D6', tools.ustr('Segmento o Unidad: %s' % lines.area_id.name), normal_format_no_border)
        date = datetime.strptime(lines.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
        worksheet.merge_range('E6:J6', tools.ustr('Fecha de Emisión: %s' % date), normal_format_no_border)

        worksheet.merge_range('A7:J7', tools.ustr('Cumplimiento de los objetivos'), normal_format_no_border)
        worksheet.set_row(6, 25)
        worksheet.write('A8', tools.ustr('No.'), merge_format)
        worksheet.merge_range('B8:G8', tools.ustr('Elementos'), merge_format)
        worksheet.merge_range('H8:I8', tools.ustr('Cantidad'), merge_format)
        worksheet.write('J8', tools.ustr('% del total'), merge_format)

        worksheet.write('A9', tools.ustr('1'), merge_format)
        worksheet.merge_range('B9:G9', tools.ustr('Cantidad de Objetivos aprobados para el año'), normal_format)
        worksheet.merge_range('H9:I9', tools.ustr(lines.objectives_amount), normal_center_format)
        worksheet.write('J9', tools.ustr(''), normal_center_format)

        worksheet.write('A10', tools.ustr('2'), merge_format)
        worksheet.merge_range('B10:G10', tools.ustr('Objetivos cumplidos hasta la fecha'), normal_format)
        worksheet.merge_range('H10:I10', tools.ustr(lines.objectives_met), normal_center_format)
        worksheet.write('J10', tools.ustr('%.2f%%' % (float(lines.objectives_met)/float(lines.objectives_amount)*100)), normal_center_format)

        worksheet.write('A11', tools.ustr('3'), merge_format)
        worksheet.merge_range('B11:G11', tools.ustr('Objetivos incumplidos hasta la fecha'), normal_format)
        worksheet.merge_range('H11:I11', tools.ustr(lines.objectives_unfulfilled), normal_center_format)
        worksheet.write('J11', tools.ustr('%.2f%%' % (float(lines.objectives_unfulfilled)/float(lines.objectives_amount)*100)), normal_center_format)

        worksheet.write('A12', tools.ustr('4'), merge_format)
        worksheet.merge_range('B12:G12', tools.ustr('Cantidad de Objetivos no evaluados hasta la fecha'), normal_format)
        worksheet.merge_range('H12:I12', tools.ustr(lines.objectives_not_evaluated), normal_center_format)
        worksheet.write('J12', tools.ustr('%.2f%%' % (float(lines.objectives_not_evaluated)/float(lines.objectives_amount)*100)), normal_center_format)

        worksheet.merge_range('A13:J13', tools.ustr('Fundamentación de objetivos incumplidos y propuestas de medidas preventivas:'), normal_format_no_border)
        worksheet.merge_range('A14:J14', tools.ustr(lines.objective_foundation if lines.objective_foundation else ''), normal_format_no_border)
        worksheet.set_row(12, 25)

        worksheet.merge_range('A16:J16', tools.ustr('Cumplimiento de la gestión de riesgos'), normal_format_no_border)
        worksheet.set_row(15, 25)
        worksheet.write('A17', tools.ustr('No.'), merge_format)
        worksheet.merge_range('B17:C17', tools.ustr('Elementos'), merge_format)
        worksheet.write('D17', tools.ustr('Cantidad'), merge_format)
        worksheet.merge_range('E17:J17', tools.ustr('% del total'), merge_format)

        worksheet.write('A18', tools.ustr('1'), merge_format)
        worksheet.merge_range('B18:C18', tools.ustr('Medidas aprobadas en el plan de prevención y gestión de riesgos'), normal_format)
        worksheet.write('D18', tools.ustr(lines.measures_approved), normal_center_format)
        worksheet.merge_range('E18:J18', tools.ustr(''), normal_center_format)

        worksheet.write('A19', tools.ustr('2'), merge_format)
        worksheet.merge_range('B19:C19', tools.ustr('Medidas a ejecutar en el mes'), normal_format)
        worksheet.write('D19', tools.ustr(lines.measures_month), normal_center_format)
        worksheet.merge_range('E19:J19', tools.ustr('%.2f%%' % (float(lines.measures_month)/float(lines.measures_approved)*100)), normal_center_format)

        worksheet.write('A20', tools.ustr('3'), merge_format)
        worksheet.merge_range('B20:C20', tools.ustr('Cumplidas'), normal_format)
        worksheet.write('D20', tools.ustr(lines.measures_accomplished), normal_center_format)
        worksheet.merge_range('E20:J20', tools.ustr('%.2f%%' % (float(lines.measures_accomplished)/float(lines.measures_approved)*100)), normal_center_format)

        worksheet.write('A21', tools.ustr('4'), merge_format)
        worksheet.merge_range('B21:C21', tools.ustr('Incumplidas'), normal_format)
        worksheet.write('D21', tools.ustr(lines.measures_unfullfilled), normal_center_format)
        worksheet.merge_range('E21:J21', tools.ustr('%.2f%%' % (float(lines.measures_unfullfilled)/float(lines.measures_approved)*100)), normal_center_format)
        worksheet.merge_range('A22:J22', tools.ustr(''), normal_center_format)
        worksheet.merge_range('A23:A24', tools.ustr('No.'), normal_center_format)
        worksheet.merge_range('B23:B24', tools.ustr('Objetivos cumplidos con medidas incumplidas'), normal_center_format)
        worksheet.merge_range('C23:C24', tools.ustr('Descripción de las medidas del plan de Prevención incumplidas'), normal_center_format)
        worksheet.merge_range('D23:D24', tools.ustr('Observaciones'), normal_center_format)
        worksheet.merge_range('E23:J23', tools.ustr('Criterios de Acciones a desarrollar en el Plan de Prevención de Riesgos'), normal_center_format)
        worksheet.write('E24', tools.ustr('Mantener'), normal_center_format)
        worksheet.write('F24', tools.ustr('Eliminar'), normal_center_format)
        worksheet.merge_range('G24:H24', tools.ustr('Modificar'), normal_center_format)
        worksheet.merge_range('I24:J24', tools.ustr('Incorporar nueva'), normal_center_format)
        worksheet.set_row(22, 30)
        worksheet.set_row(23, 30)

        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 22)
        worksheet.set_column('C1:C1', 18)
        worksheet.set_column('D1:D1', 18)
        worksheet.set_column('E1:E1', 10)
        worksheet.set_column('F1:F1', 10)
        worksheet.set_column('G1:G1', 5)
        worksheet.set_column('H1:H1', 5)
        worksheet.set_column('I1:I1', 5)
        worksheet.set_column('J1:I1', 8)

        i = 24
        count = 1
        for record in lines.line_ids:
            worksheet.write(i, 0, tools.ustr(count), normal_center_format)
            worksheet.write(i, 1, tools.ustr(record.objective if record.objective else ''), normal_center_format)
            worksheet.write(i, 2, tools.ustr(record.measures_not_complied if record.measures_not_complied else ''), normal_center_format)
            worksheet.write(i, 3, tools.ustr(record.observations if record.observations else ''), normal_center_format)
            worksheet.write(i, 4, tools.ustr('X' if record.action == 'keep' else ''), normal_center_format)
            worksheet.write(i, 5, tools.ustr('X' if record.action == 'delete' else ''), normal_center_format)
            worksheet.merge_range(i, 6, i, 7, tools.ustr('X' if record.action == 'modify' else ''), normal_center_format)
            worksheet.merge_range(i, 8, i, 9, tools.ustr('X' if record.action == 'incorporate' else ''), normal_center_format)
            i += 1
            count += 1

        worksheet.merge_range(i + 1, 0, i + 1, 9, tools.ustr('Incidencias Evaluadas:'), normal_format_no_border)
        worksheet.merge_range(i + 2, 0, i + 2, 9,tools.ustr(lines.evaluated_incidents if lines.evaluated_incidents else ''), normal_format_no_border)
        worksheet.set_row(i + 1, 25)

        worksheet.merge_range(i + 4, 0, i + 4, 9, tools.ustr('Detección del Cambio:'), normal_format_no_border)
        worksheet.merge_range(i + 5, 0, i + 5, 9,tools.ustr(lines.change_detection if lines.change_detection else ''), normal_format_no_border)
        worksheet.set_row(i + 4, 25)

        worksheet.merge_range(i + 7, 0, i + 7, 9, tools.ustr('Propuestas de acuerdos:'), normal_format_no_border)
        worksheet.merge_range(i + 8, 0, i + 8, 9,tools.ustr(lines.proposed_agreements if lines.proposed_agreements else ''), normal_format_no_border)
        worksheet.set_row(i + 7, 25)

        worksheet.merge_range(i + 10, 0, i + 10, 3, tools.ustr('Elaborado por:'), normal_format_no_border)
        worksheet.merge_range(i + 11, 0, i + 11, 3,tools.ustr(lines.elaborates_id.name if lines.elaborates_id else ''), normal_format_no_border)

        worksheet.merge_range(i + 10, 4, i + 10, 9, tools.ustr('Aprobado por:'), normal_format_no_border)
        worksheet.merge_range(i + 11, 4, i + 11, 9,tools.ustr(lines.approve_id.name if lines.approve_id else ''), normal_format_no_border)


BehaviorPreventionPlan('report.enterprise_mgm_sys.behavior_prevention_plan_report', 'enterprise_mgm_sys.behavior_prevention_plan')

