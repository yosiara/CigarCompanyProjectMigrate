# -*- coding: utf-8 -*-
import xlsxwriter
from odoo import models, fields, api, tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.http import addons_manifest
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class CompliancePannedEfficiencyToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        productive_sections = self.env['turei_process_control.productive_section'].search([('active', '=', True)], order="name ASC")
        turns = self.env['resource.calendar'].search([('turn_process_control', '=', True)])
        if not productive_sections:
            self.env.user.notify_info(tools.ustr('No existen datos que mostrar.'))
            return

        worksheet = workbook.add_worksheet("Cumplimiento de eficiencia planificada")

        worksheet.insert_textbox('A1:K1', tools.ustr("EMPRESA DE CIGARRO LAZARO PEÑA"), options={'font': {'color': 'black',
                                                                                                          'size': 12, 'bold': 1}, 'width': 550, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                                                                                 'line': {'none': True}})
        worksheet.insert_textbox('A2:K2', tools.ustr("CUMPLIMIENTO DE EFICIENCIA PLANIFICADA (DESDE %s HASTA %s)") % (lines.date_start, lines.date_end),
                                 options={'y_offset': 0, 'font': {'color': 'black', 'bold': 1,
                                                                  'size': 10}, 'width': 730, 'x_offset': 15, 'height': 10, 'fill': {'none': True},
                                          'line': {'none': True}})
        worksheet.insert_image('K1', addons_manifest['turei_process_control']['addons_path'] + '/turei_process_control/static/src/img/logo_hoja.png', {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.set_column('A4:I4', 10)
        worksheet.set_column('B4:C4', 20)
        worksheet.set_column('E4:E4', 20)
        worksheet.set_column('G4:I4', 20)
        worksheet.write('A4', tools.ustr('SP'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('B4', tools.ustr('Plan  (caj.)'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('C4', tools.ustr('Eficiencia Plan (%) '), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        row = 3
        for turn in turns:
            worksheet.write(3, row, tools.ustr(turn.name.capitalize()), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
            row += 1
            worksheet.write(3, row, tools.ustr('Desv. ' + turn.name.capitalize()), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
            row += 1
        worksheet.write('H4', tools.ustr('Total'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))
        worksheet.write('I4', tools.ustr('Desv. Total'), workbook.add_format({'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 12}}))

        row = 4
        for productive_section in productive_sections:
            worksheet.write(row, 0, str(productive_section.name[-2:]), workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            section_plan = productive_section.get_efficiency_plan()
            plan_c = 0.00
            plan_eff = 0.00
            if section_plan:
                if len(section_plan) == 1:
                    plan_c = section_plan.indice_planif_norma
                    plan_eff = section_plan.indice_planif_efici_real
                elif len(section_plan) > 1:
                    for plan in section_plan:
                        plan_c += plan.indice_planif_norma
                        plan_eff += plan.indice_planif_efici_real
                worksheet.write_number(row, 1, plan_c, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                worksheet.write_number(row, 2, plan_eff, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            else:
                worksheet.write_number(row, 1, 0.00, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                worksheet.write_number(row, 2, 0.00, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))

            index = 3
            sum_eff = 0.00
            sum_dev_eff = 0.00
            for turn in turns:
                efficiency = productive_section.calculate_efficiency(lines.date_start, lines.date_end, turn.id)
                sum_eff += efficiency
                worksheet.write_number(row, index, efficiency, workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                index += 1
                sum_dev_eff += efficiency - plan_eff
                if efficiency - plan_eff >= 0:
                    worksheet.write_number(row, index, round(efficiency - plan_eff, 2), workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                else:
                    worksheet.write_number(row, index, round(efficiency - plan_eff, 2), workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
                index += 1
            if sum_eff >= 0:
                worksheet.write_number(row, index, round(sum_eff / len(turns), 2), workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            else:
                worksheet.write_number(row, index, round(sum_eff / len(turns), 2), workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            index += 1
            if sum_dev_eff >= 0:
                worksheet.write_number(row, index, round(sum_dev_eff / len(turns), 2), workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            else:
                worksheet.write_number(row, index, round(sum_dev_eff / len(turns), 2), workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 12}}))
            row += 1


CompliancePannedEfficiencyToExcelReport('report.turei_process_control.compliance_planned_efficiency', 'wzd.compliance.planned.efficiency.excel')
