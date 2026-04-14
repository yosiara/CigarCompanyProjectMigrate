# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class XlsReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data,lines):

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font_size': 8, 'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri'})
        merge_format1 = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font_size': 8, 'bg_color': '#E78B93', 'font_color': '#000000', 'font_name': 'Calibri'})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 8,'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri'})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font_size': 10,'bg_color': '#FC5E6C'})

        worksheet = workbook.add_worksheet(tools.ustr('Candidatos a verificar'))

        applicant_ids = self.env['hr.applicant'].search([('job_id','=',lines.job_id.id),('estado','=','proceso')])

        worksheet.merge_range('C1:G1', tools.ustr("Candidatos a verificar para "+lines.job_id.name), head_format)
        worksheet.set_column('A3:A3', 9)
        worksheet.set_column('B3:B3', 17)
        worksheet.set_column('C3:C3', 35)
        worksheet.set_column('D3:D3', 8)
        worksheet.set_column('E3:E3', 8)
        worksheet.set_column('F3:F3', 10)
        worksheet.set_column('G3:G3', 20)
        worksheet.set_column('H3:G3', 20)


        worksheet.write('A3', tools.ustr('Carnet de ID'), merge_format1)
        worksheet.write('B3', tools.ustr('Nombre'), merge_format1)
        worksheet.write('C3', tools.ustr('Dirección Particular'), merge_format1)
        worksheet.write('D3', tools.ustr('Télefono Fijo'), merge_format1)
        worksheet.write('E3', tools.ustr('Télefono Móvil'), merge_format1)
        worksheet.write('F3', tools.ustr('Correo Electrónico'), merge_format1)
        worksheet.write('G3', tools.ustr('Ubicación Laboral Actual'), merge_format1)
        worksheet.write('H3', tools.ustr('Carrera'), merge_format1)

        x = 3
        for c in applicant_ids:
            worksheet.write(x, 0, tools.ustr(c.ci), normal_format)
            worksheet.write(x, 1, tools.ustr(c.partner_name), normal_format)
            worksheet.write(x, 2, tools.ustr(c.direccion_particular), normal_format)
            if c.applicant_phone:
                worksheet.write(x, 3, tools.ustr(c.applicant_phone), normal_format)
            else:
                worksheet.write(x, 3, tools.ustr(''), normal_format)
            if c.applicant_mobile:
                worksheet.write(x, 4, tools.ustr(c.applicant_mobile), normal_format)
            else:
                worksheet.write(x, 4, tools.ustr(''), normal_format)
            if c.applicant_email:
                worksheet.write(x, 5, tools.ustr(c.applicant_email), normal_format)
            else:
                worksheet.write(x, 5, tools.ustr(''), normal_format)
            worksheet.write(x, 6, tools.ustr(c.ubicacion_laboral_actual), normal_format)
            if c.degree_id:
                worksheet.write(x, 7, tools.ustr(c.degree_id.name), normal_format)
            else:
                worksheet.write(x, 7, tools.ustr(''), normal_format)
            x += 1



XlsReport('report.app_seleccion.xls_report', 'app_seleccion.xls_report')
