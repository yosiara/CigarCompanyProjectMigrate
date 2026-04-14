# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import xlwt


class XlsReportCyears(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data,lines):

        candidatos_total = self.env['hr.applicant'].search_count([('year','=',int(lines.year))])
        candidatos_aprobados = self.env['hr.applicant'].search_count([('year','=',int(lines.year)),('estado','=','aprobado')])
        candidatos_aprobados_curso = self.env['hr.applicant'].search_count([('year','=',int(lines.year)),('estado','=','curso')])
        candidatos_aprobados_reserva = self.env['hr.applicant'].search_count([('year','=',int(lines.year)),('estado','=','reserva')])
        candidatos_rechazados = self.env['hr.applicant'].search_count([('year','=',int(lines.year)),('estado','=','rechazado')])
        candidatos_proceso = self.env['hr.applicant'].search_count([('year','=',int(lines.year)),('estado','=','proceso')])

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri'})
        merge_format1 = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#FFFF33', 'font_color': '#000000', 'font_name': 'Calibri'})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 10}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        worksheet = workbook.add_worksheet(tools.ustr('Comportamiento'))
        worksheet.merge_range('D1:J1', tools.ustr("Comportamiento del Proceso de Seleccion en "+lines.year), head_format)
        bold = workbook.add_format({'bold': 1})


        # Add the worksheet data that the charts will refer to.
        headings = ['Categorias', 'Valores']
        data = [
        ['Procesados', 'Aprobados para Puesto de Trabajo', 'Aprobados para Curso', 'Aprobados para reserva', 'No aprobados','En proceso'],
        [candidatos_total,candidatos_aprobados,candidatos_aprobados_curso,candidatos_aprobados_reserva,candidatos_rechazados, candidatos_proceso], ]

        worksheet.set_column('A3:A3', 30)
        worksheet.write_row('A2', headings, bold)
        worksheet.write_column('A3', data[0])
        worksheet.write_column('B3', data[1])

        chart1 = workbook.add_chart({'type': 'pie'})

        # Configure the series. Note the use of the list syntax to define ranges:
        chart1.add_series({
            'name':       'Comportamiento del Proceso de Seleccion',
            'categories': '=Comportamiento!$A$4:$A$8',
            'values':     '=Comportamiento!$B$4:$B$8',
            })

        # Add a title.
        chart1.set_title({'name': 'Comportamiento del Proceso de Seleccion en '+lines.year})

        # Set an Excel chart style. Colors with white outline and shadow.
        chart1.set_style(10)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('C2', chart1, {'x_offset': 35, 'y_offset': 10})




        workbook.close()




XlsReportCyears('report.app_seleccion.xls_report_cyears', 'app_seleccion.xls_report_cyears')
