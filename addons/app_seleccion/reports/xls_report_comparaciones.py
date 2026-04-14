# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import xlwt


class XlsReportComparaciones(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data,lines):
        #buscar cada año
        sql = "select DISTINCT YEAR from hr_applicant"

        self.env.cr.execute(sql,)
        years = self.env.cr.fetchall()

        lista_candidatos_total = []
        lista_candidatos_aprobados = []
        lista_candidatos_aprobados_curso = []
        lista_candidatos_aprobados_reserva = []
        lista_candidatos_rechazados = []
        lista_candidatos_proceso = []

        #debo hacer las consultas para cada año
        for year in years:
            candidatos_total = self.env['hr.applicant'].search_count([('year','=',year)])
            lista_candidatos_total.append(candidatos_total)
            candidatos_aprobados = self.env['hr.applicant'].search_count([('year','=',year),('estado','=','aprobado')])
            lista_candidatos_aprobados.append(candidatos_aprobados)
            candidatos_aprobados_curso = self.env['hr.applicant'].search_count([('year','=',year),('estado','=','curso')])
            lista_candidatos_aprobados_curso.append(candidatos_aprobados_curso)
            candidatos_aprobados_reserva = self.env['hr.applicant'].search_count([('year','=',year),('estado','=','reserva')])
            lista_candidatos_aprobados_reserva.append(candidatos_aprobados_reserva)
            candidatos_rechazados = self.env['hr.applicant'].search_count([('year','=',year),('estado','=','rechazado')])
            lista_candidatos_rechazados.append(candidatos_rechazados)
            candidatos_proceso = self.env['hr.applicant'].search_count([('year','=',year),('estado','=','proceso')])
            lista_candidatos_proceso.append(candidatos_proceso)

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri'})
        merge_format1 = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#FFFF33', 'font_color': '#000000', 'font_name': 'Calibri'})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 10}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        worksheet = workbook.add_worksheet(tools.ustr('Comparaciones'))
        worksheet.merge_range('D1:J1', tools.ustr("Proceso de Seleccion"), head_format)
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




XlsReportComparaciones('report.app_seleccion.xls_report_comparaciones', 'app_seleccion.xls_report_comparaciones')
