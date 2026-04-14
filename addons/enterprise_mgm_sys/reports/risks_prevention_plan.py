# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class RisksPreventionPlan(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet(tools.ustr('Plan de prevención de riesgos'))
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
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
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
        worksheet.merge_range('C1:H3', tools.ustr('Plan de Prevención y gestión de riesgos (R-2)'), merge_format)
        worksheet.merge_range('A1:B3', tools.ustr(''), merge_format)
        worksheet.merge_range('I1:J1', tools.ustr('Versión: 00'), identification_format)
        worksheet.merge_range('I2:J2', tools.ustr('Fecha de aprobación: 21/6/2018'), identification_format)
        worksheet.merge_range('I3:J3', tools.ustr('Código: M-DTD-03-R16'), identification_format)
        worksheet.merge_range('A6:E6', tools.ustr('Segmento o Unidad: %s' % lines.area_id.name), normal_format_no_border)
        date = datetime.strptime(lines.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
        worksheet.merge_range('F6:J6', tools.ustr('Fecha de realización: %s' % date), normal_format_no_border)

        worksheet.write('A8', tools.ustr('No'), merge_format)
        worksheet.write('B8', tools.ustr('Objetivos'), merge_format)
        worksheet.write('C8', tools.ustr('Procesos'), merge_format)
        worksheet.write('D8', tools.ustr('Actividad'), merge_format)
        worksheet.write('E8', tools.ustr('Riesgo'), merge_format)
        worksheet.write('F8', tools.ustr('Posibles manifestaciones negativas'), merge_format)
        worksheet.write('G8', tools.ustr('Medidas '), merge_format)
        worksheet.write('H8', tools.ustr('Responsable'), merge_format)
        worksheet.write('I8', tools.ustr('Ejecutan '), merge_format)
        worksheet.write('J8', tools.ustr('F/C'), merge_format)

        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 22)
        worksheet.set_column('C1:C1', 18)
        worksheet.set_column('D1:D1', 18)
        worksheet.set_column('E1:E1', 18)
        worksheet.set_column('F1:F1', 18)
        worksheet.set_column('G1:G1', 18)
        worksheet.set_column('H1:H1', 18)
        worksheet.set_column('I1:I1', 18)
        worksheet.set_column('J1:I1', 14)

        i = 8
        count = 1
        for record in lines.measure_ids:
            worksheet.write(i, 0, tools.ustr(count), normal_format)
            worksheet.write(i, 1, tools.ustr(record.objective if record.objective else ''), normal_format)
            worksheet.write(i, 2, tools.ustr(record.process_id.name if record.process_id.name else ''), normal_format)
            worksheet.write(i, 3, tools.ustr(record.activity_id.name if record.activity_id.name else ''), normal_format)
            worksheet.write(i, 4, tools.ustr(record.risk_id.name if record.risk_id.name else ''), normal_format)
            worksheet.write(i, 5, tools.ustr(record.manifestations if record.manifestations else ''), normal_format)
            worksheet.write(i, 6, tools.ustr(record.measures if record.measures else ''), normal_format)
            worksheet.write(i, 7, tools.ustr(record.employee_id.job_id.name if record.employee_id.job_id else record.employee_id.name), normal_format)
            worksheet.write(i, 8, tools.ustr(self._get_execute(record)), normal_format)
            worksheet.write(i, 9, tools.ustr(record.compliance_dates if record.compliance_dates else ''), normal_format)
            i += 1
            count += 1

    def _get_execute(self, line):
        if line.execute_use_employees:
            execute = ''
            for employee in line.execute_ids:
                if employee.job_id:
                    execute += employee.job_id.name + ', '
                else:
                    execute += employee.name + ', '
            return execute
        else:
            return line.execute if line.execute else ''

RisksPreventionPlan('report.enterprise_mgm_sys.risks_prevention_plan_report', 'enterprise_mgm_sys.risks_prevention_plan')
