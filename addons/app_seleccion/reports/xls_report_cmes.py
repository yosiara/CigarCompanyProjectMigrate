# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import xlwt


class XlsReportCmes(ReportXlsx):

    @staticmethod
    def get_nombre_mes(mes):
        if mes == '01':
            return 'enero'
        elif mes == '02':
            return 'febrero'
        elif mes == '03':
            return 'marzo'
        elif mes == '04':
            return 'abril'
        elif mes == '05':
            return 'mayo'
        elif mes == '06':
            return 'junio'
        elif mes == '07':
            return 'julio'
        elif mes == '08':
            return 'agosto'
        elif mes == '09':
            return 'septiembre'
        elif mes == '10':
            return 'octubre'
        elif mes == '11':
            return 'noviembre'
        elif mes == '12':
            return 'diciembre'

    @api.model
    def generate_xlsx_report(self, workbook, data,lines):

        candidatos_total = self.env['hr.applicant'].search_count([('mes','=',lines.mes),('year','=',int(lines.year))])
        candidatos_aprobados = self.env['hr.applicant'].search_count([('mes','=',lines.mes),('year','=',int(lines.year)),('estado','=','aprobado')])
        candidatos_aprobados_curso = self.env['hr.applicant'].search_count([('mes','=',lines.mes),('year','=',int(lines.year)),('estado','=','curso')])
        candidatos_aprobados_reserva = self.env['hr.applicant'].search_count([('mes','=',lines.mes),('year','=',int(lines.year)),('estado','=','reserva')])
        candidatos_rechazados = self.env['hr.applicant'].search_count([('mes','=',lines.mes),('year','=',int(lines.year)),('estado','=','rechazado')])
        candidatos_proceso = self.env['hr.applicant'].search_count([('mes','=',lines.mes),('year','=',int(lines.year)),('estado','=','proceso')])

        sql_expertos_total = "SELECT count(hr_applicant.name) FROM (hr_applicant INNER JOIN app_seleccion_solicitud_expertos_hr_applicant_rel ON" \
                             " hr_applicant.id = app_seleccion_solicitud_expertos_hr_applicant_rel.hr_applicant_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_applicant_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.mes_experto = %s and app_seleccion_solicitud_expertos.year = %s"
        self.env.cr.execute(sql_expertos_total,(lines.mes,lines.year))
        total_expertos = self.env.cr.fetchone()

        #de fuente interna
        sql_expertos_total_internos = "SELECT count(hr_employee.name_related) FROM (hr_employee INNER JOIN app_seleccion_solicitud_expertos_hr_employee_rel ON" \
                             " hr_employee.id = app_seleccion_solicitud_expertos_hr_employee_rel.hr_employee_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_employee_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.mes_experto = %s and app_seleccion_solicitud_expertos.year = %s"
        self.env.cr.execute(sql_expertos_total_internos,(lines.mes,lines.year))
        total_expertos_internos = self.env.cr.fetchone()

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri'})
        merge_format1 = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#FFFF33', 'font_color': '#000000', 'font_name': 'Calibri'})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 10}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        worksheet = workbook.add_worksheet(tools.ustr('Comportamiento'))
        worksheet.merge_range('D1:J1', tools.ustr("Comportamiento del Proceso de Seleccion en "+self.get_nombre_mes(lines.mes))+" de "+lines.year, head_format)
        bold = workbook.add_format({'bold': 1})


        # Add the worksheet data that the charts will refer to.
        headings = ['Categorias', 'Valores']
        data = [
        ['Procesados de nuevo Ingreso', 'Aprobados para Puesto de Trabajo', 'Aprobados para Curso', 'Aprobados para reserva', 'No aprobados','En proceso','En Comite de Expertos'],
        [candidatos_total,candidatos_aprobados,candidatos_aprobados_curso,candidatos_aprobados_reserva,candidatos_rechazados, candidatos_proceso, total_expertos[0]+total_expertos_internos[0]], ]

        worksheet.set_column('A3:A3', 30)
        worksheet.write_row('A2', headings, bold)
        worksheet.write_column('A3', data[0])
        worksheet.write_column('B3', data[1])

        chart1 = workbook.add_chart({'type': 'pie'})

        # Configure the series. Note the use of the list syntax to define ranges:
        chart1.add_series({
            'name':       'Comportamiento del Proceso de Seleccion',
            'categories': '=Comportamiento!$A$4:$A$9',
            'values':     '=Comportamiento!$B$4:$B$9',
            })

        # Add a title.
        chart1.set_title({'name': 'Comportamiento'})

        # Set an Excel chart style. Colors with white outline and shadow.
        chart1.set_style(10)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('C2', chart1, {'x_offset': 55, 'y_offset': 20})




        workbook.close()




XlsReportCmes('report.app_seleccion.xls_report_cmes', 'app_seleccion.xls_report_cmes')
