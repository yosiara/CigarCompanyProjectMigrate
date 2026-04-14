# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class EfficacyEvaluationReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Evaluación Eficacia'))
        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})

        worksheet.set_column('B2:C3', 11)
        worksheet.merge_range('B2:C3', tools.ustr(""), merge_format)
        worksheet.insert_image('B2:C3', addons_manifest['turei_maintenance']['addons_path'] + '/turei_maintenance/static/src/img/tabacuba.jpg',
                               {'x_offset': 15, 'x_scale': 1, 'y_scale': 1})
        worksheet.merge_range('D2:G3', tools.ustr("REGISTRO EVALUACIÓN DE LA EFICACIA"), merge_format)
        worksheet.merge_range('H2:I2', lines.date_end, merge_format)
        worksheet.merge_range('H2:I2', tools.ustr("Cód:MP-R-DTD-29"), merge_format)
        worksheet.merge_range('H3:I3', tools.ustr("Fecha:%s") %(lines.date_end), merge_format)
        worksheet.merge_range('J2:K3', tools.ustr("Proceso: Mantenimiento a la industria"), merge_format)
        worksheet.merge_range('L2:N2', tools.ustr("Período evaluado: %s") % (fields.Date.from_string(lines.date_start).strftime("%B")), merge_format)
        worksheet.merge_range('L3:N3', tools.ustr("Fecha de entrega: %s") % (datetime.now().date()), merge_format)
        worksheet.write('B4', tools.ustr('No.'), merge_format)
        worksheet.set_column('C4:D4', 25)
        worksheet.merge_range('C4:D4', tools.ustr('Indicadores'), merge_format)
        worksheet.set_column('E4:E4', 35)
        worksheet.write('E4', tools.ustr('Fuente de Información'), merge_format)
        worksheet.write('F4', tools.ustr('Frecuencia'), merge_format)
        worksheet.write('G4', tools.ustr('U/M'), merge_format)
        worksheet.write('H4', tools.ustr('Valor Óptimo'), merge_format)
        worksheet.write('I4', tools.ustr('Eficaz (5ptos)'), merge_format)
        worksheet.write('J4', tools.ustr('No Eficaz (2ptos)'), merge_format)
        worksheet.write('K4', tools.ustr('Evaluación'), merge_format)
        worksheet.write('L4', tools.ustr('Puntuación'), merge_format)
        worksheet.write('M4', tools.ustr('Peso'), merge_format)
        worksheet.write('N4', tools.ustr('Valor alcanzado'), merge_format)

        evaluation_parameter = self.env['turei_maintenance.evaluation_parameter'].search([])
        productive_section = self.env['turei_process_control.productive_section'].search([])
        productive_line_primary = self.env['process_control_primary.productive_line'].search([])

        cdt = 0.00
        for ps in productive_section:
            cdt += ps.calculate_cdt(lines.date_start, lines.date_end)
        cdt_secundary = cdt / len(productive_section)

        cdt_p = 0.00
        for pl in productive_line_primary:
            cdt_p += pl.calculate_cdt(lines.date_start, lines.date_end)
        cdt_primary = cdt_p / len(productive_line_primary)
        

        # tecnolog_control = self.env['process_control_tobacco.tecnolog_control_model'].search([('date', '>=', lines.date_start), ('date', '<=', lines.date_end)], order='date, turn')
        # tti, s_plan_time = 0.00, 0.00
        # for tc in tecnolog_control:
        #     s_plan_time += tc.plan_time
        #     for it in tc.interruptions:
        #         tti += it.time
        # cdt_tobacco = round(((s_plan_time - (tti / 60)) / s_plan_time) * 100, 2)

        # cdt_industry = round((cdt_primary + cdt_secundary + cdt_tobacco) / 3, 2)
        cdt_industry = round((cdt_primary + cdt_secundary) / 2, 2)

        planif_count = self.env['turei_maintenance.work_order'].search_count(['|', ('work_type', '=', 'plan_ciclo'), ('work_type', '=', 'plan_et'), ('opening_date', '>=', lines.date_start), ('opening_date', '<=', lines.date_end)])
        imprev_count = self.env['turei_maintenance.work_order'].search_count([('work_type', '=', 'imp-tec'), ('opening_date', '>=', lines.date_start), ('opening_date', '<=', lines.date_end)])

        x, cont = 4, 1
        for ef in evaluation_parameter.efficacy_evaluation_ids:
            worksheet.write(x, 1, cont, normal_format)
            worksheet.merge_range(x, 2, x, 3, tools.ustr(ef.name), normal_format)
            worksheet.write(x, 5, tools.ustr("Mensual"), normal_format)
            worksheet.write(x, 6, tools.ustr("%"), normal_format)
            worksheet.write(x, 7, ef.value_opt, normal_format)
            worksheet.write(x, 8, ef.comp_value_efficacy, normal_format)
            worksheet.write(x, 9, ef.comp_value_no_efficacy, normal_format)
            worksheet.write(x, 12, ef.value_weight, normal_format)
            x += 1
            cont += 1

        worksheet.write(4, 10, cdt_industry, normal_format)
        worksheet.write(5, 10, 100, normal_format)
        imp_plan = round(imprev_count/planif_count, 2)
        worksheet.write(6, 10, imp_plan, normal_format)
        if cdt_industry < evaluation_parameter.efficacy_evaluation_ids[0].value_no_efficacy:
            punt1 = 2
        else:
            punt1 = 5
        worksheet.write(4, 11, punt1, normal_format)
        if 100 < evaluation_parameter.efficacy_evaluation_ids[1].value_no_efficacy:
            punt2 = 2
        else:
            punt2 = 5
        worksheet.write(5, 11, punt2, normal_format)
        if imp_plan >= 1:
            punt3 = 2
        else:
            punt3 = 5
        worksheet.write(6, 11, punt3, normal_format)

        worksheet.write(4, 13, punt1 * evaluation_parameter.efficacy_evaluation_ids[0].value_weight, normal_format)
        worksheet.write(5, 13, punt2 * evaluation_parameter.efficacy_evaluation_ids[0].value_weight, normal_format)
        worksheet.write(6, 13, punt3 * evaluation_parameter.efficacy_evaluation_ids[2].value_weight, normal_format)

        worksheet.write(7, 10, tools.ustr("TOTAL"), merge_format)
        sum_val_a = (punt1 * evaluation_parameter.efficacy_evaluation_ids[0].value_weight) + (punt2 * evaluation_parameter.efficacy_evaluation_ids[0].value_weight) + (punt3 * evaluation_parameter.efficacy_evaluation_ids[2].value_weight)
        val_ef = round((sum_val_a / evaluation_parameter[0].value_opt) * 100, 2)
        worksheet.write(7, 11, val_ef,normal_format)
        worksheet.write(7, 12, tools.ustr("Valor real"), merge_format)
        worksheet.write(7, 13, sum_val_a, normal_format)

        worksheet.write(8, 10, tools.ustr("EFICACIA"), merge_format)
        if val_ef >= evaluation_parameter[0].cohef_maint:
            efficency = 'EFICAZ'
        else:
            efficency = 'NO EFICAZ'
        worksheet.write(8, 11, tools.ustr(efficency), normal_format)
        worksheet.write(8, 12, tools.ustr("Valor óptimo"), merge_format)
        worksheet.write(8, 13, evaluation_parameter[0].value_opt, normal_format)

        worksheet.merge_range('B11:J11', tools.ustr("CRITERIO DE EVALUACIÓN"), merge_format)
        worksheet.merge_range('B12:J12', tools.ustr("El proceso de mantenimiento a la industria es eficaz si obtiene una puntuación: %s") % (evaluation_parameter[0].comp_value_efficacy_industry), merge_format)

        worksheet.write(4, 4, tools.ustr("Ttotal Planif - Ttotal de Interrupciones / Ttotal Planif * 100"), normal_format)
        worksheet.write(5, 4, tools.ustr("Real / Plan * 100"), normal_format)
        worksheet.write(6, 4, tools.ustr("Cant Imprevisto / Cant Acciones Planificadas"), normal_format)

EfficacyEvaluationReport('report.turei_maintenance.efficacy_evaluation_report', 'wzd.efficacy.evaluation')
