# -*- coding: utf-8 -*-
from StringIO import StringIO
from datetime import datetime
from odoo import models, api, fields
import sys
import xlwt
from xlwt import *
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.http import addons_manifest
from ..models.excel_base import ExcelBase
from odoo import models, fields, api, tools

reload(sys)
sys.setdefaultencoding("utf-8")

FONT_SIZE = 8
DATE_FORMAT = "%d/%m/%Y"

class ReportEmployeeExcel(ExcelBase):
    def __init__(self, model, cr, uid, context=None):
        ExcelBase.__init__(self, model, cr, uid, context=context)

    @api.multi
    def print_table1(self, ws, row=0):
        """ Print Header 1"""
        borders1 = Borders()
        borders1.left = 1
        borders1.right = 1
        borders1.top = 1
        borders1.bottom = 1

        borders2 = Borders()
        borders2.left = 0
        borders2.right = 0
        borders2.top = 0
        borders2.bottom = 0

        al_center = Alignment()
        al_center.horz = Alignment.HORZ_CENTER
        al_center.vert = Alignment.VERT_CENTER
        al_center.wrap = Alignment.WRAP_AT_RIGHT

        al_left = Alignment()
        al_left.horz = Alignment.HORZ_LEFT
        al_left.vert = Alignment.VERT_CENTER
        al_left.wrap = Alignment.WRAP_AT_RIGHT

        al_right = Alignment()
        al_right.horz = Alignment.HORZ_RIGHT
        al_right.vert = Alignment.VERT_CENTER
        al_right.wrap = Alignment.WRAP_AT_RIGHT

        fnt1 = Font()
        fnt2 = Font()
        fnt3 = Font()
        fnt4 = Font()
        fnt5 = Font()
        fnt4.height = self.font_size(12)
        fnt5.height = self.font_size(11)
        fnt1.height = self.font_size(11)
        fnt1.bold = True
        fnt2.bold = False
        fnt3.bold = False
        fnt4.bold = True
        fnt5.bold = True
        style1 = XFStyle()
        style2 = XFStyle()
        style3 = XFStyle()
        style4 = XFStyle()
        style5 = XFStyle()
        style6 = XFStyle()

        style1.borders = borders1
        style1.font = fnt1
        style1.alignment = al_right
        style2.borders = borders1
        style2.font = fnt1
        style2.alignment = al_left
        style3.borders = borders1
        style3.font = fnt2
        style3.alignment = al_left
        style4.borders = borders1
        style4.font = fnt5
        style4.alignment = al_right
        style5.borders = borders1
        style5.font = fnt5
        style5.alignment = al_center
        style6.borders = borders2
        style6.font = fnt4
        style6.alignment = al_center


        xlwt.add_palette_colour("gris", 0x21)
        self.workbook.set_colour_RGB(0x21, 217, 217, 217)


        ws.write_merge(0, 0, 0, 13, "Tabla para informar trabajadores que no se pueden incorporar al Sistema Informatico GeForza", style6)

        row += 4

        ws.write(row, 0, 'NO', style5)
        ws.write(row, 1, '1er Nombre', style5)
        ws.write(row, 2, '2do Nombre', style5)
        ws.write(row, 3, '1er Apellido', style5)
        ws.write(row, 4, '2do Apellido', style5)
        ws.write_merge(row, row, 5, 6, 'Carnet de Identidad', style5)
        ws.write(row, 7, 'Edad', style5)
        ws.write(row, 8, 'Sexo', style5)
        ws.write(row, 9, 'Provincia', style5)
        ws.write(row, 10, 'Municipio', style5)
        ws.write_merge(row, row, 11, 12,  'Tipo de Contrato', style5)
        ws.write(row, 13, 'Fecha de Alta en la Unidad', style5)
        ws.write(row, 14, 'Categoría Ocupacional', style5)
        ws.write_merge(row, row, 15, 16,  'Carrera de graduados', style5)

        #list employees
        employees = self.model.env['hr.employee'].search([('id','in',self.model.employee_some.ids)])

        row += 1

        i = 0
        counter_primary = 0
        counter_secondary = 0
        counter_qualify_worker = 0
        counter_pre_university = 0
        counter_middle_level = 0
        counter_high_level = 0
        counter_all = 0
        for employee in employees:
            ws.write(row, 0, i + 1, style3)
            ws.write(row, 1,tools.ustr(employee.first_name),style3)
            ws.write(row, 2, tools.ustr(''), style3)
            ws.write(row, 3, tools.ustr(employee.last_name), style3)
            ws.write(row, 4, tools.ustr(employee.second_last_name), style3)
            ws.write_merge(row, row, 5, 6, tools.ustr(employee.identification_id), style3)
            ws.write(row, 7, tools.ustr(employee.age), style3)

            sexo = 'M'
            if employee.gender == 'female':
                sexo = 'F'
            ws.write(row, 8, tools.ustr(sexo), style3)
            ws.write(row, 9, tools.ustr(self.model.env.user.company_id.state_id.name), style3)
            ws.write(row, 10, tools.ustr(self.model.env.user.company_id.partner_id.municipality_id.name), style3)

            contract_type = self.model.env['l10n_cu_hlg_hr_work_force.contract_hr_type'].search([('id', '=', employee.contract_hr_type_id.id)],limit=1).code

            if contract_type == 'I':
                ws.write_merge(row, row, 11, 12, 'Indeterminado', style3)
            else:
                ws.write_merge(row, row, 11, 12, 'Determinado', style3)

            ws.write(row, 13, tools.ustr(employee.admission_date), style3)
            category = 'Obreros'
            if employee.occupational_category_id.name == 'A':
                category = 'Administrativos'
            elif employee.occupational_category_id.name == 'T':
                category = 'Técnicos'
            elif employee.occupational_category_id.name == 'Operario':
                category = 'Obreros'
            elif employee.occupational_category_id.name == 'S':
                category = 'Servicios'
            elif employee.occupational_category_id.name == 'C':
                category = 'Cuadros'
            else:
                category = 'Obreros'

            if employee.school_level_id.external_id == '001' or employee.school_level_id.external_id == '002' or employee.school_level_id.external_id == '002' or employee.school_level_id.external_id == '003' or employee.school_level_id.external_id == '004' or employee.school_level_id.external_id == '005' or employee.school_level_id.external_id == '006':
                counter_primary += 1
            elif employee.school_level_id.external_id == '007' or employee.school_level_id.external_id == '008' or employee.school_level_id.external_id == '009' or employee.school_level_id.code == '1':
                counter_secondary += 1
            elif employee.school_level_id.external_id == '010' or employee.school_level_id.external_id == '011' or employee.school_level_id.external_id == '012' or employee.school_level_id.code == '3':
                counter_pre_university += 1
            elif employee.school_level_id.external_id == 'TMD':
                counter_middle_level += 1
            elif employee.school_level_id.external_id == 'FOC' or employee.school_level_id.code == '2020':
                counter_qualify_worker += 1
            elif employee.school_level_id.external_id == 'UNI' or employee.school_level_id.code == 'UNI':
                counter_high_level += 1

            ws.write(row, 14, tools.ustr(category), style3)
            ws.write_merge(row, row, 15, 16, tools.ustr(employee.degree_id.name), style3)
            i += 1
            counter_all += 1
            row += 1

        row += 2

        ws.write_merge(row + 1, row + 1, 0, 15,"Tabla para informar la cantidad de trabajadores por nivel de enseñanza (de los trabajadores que no se pudieron incorporar al Geforza)",
                       style6)
        row += 3
        ws.write_merge(row, row, 1, 2, 'Nivel Académico', style5)
        ws.write_merge(row, row, 3, 4, 'De esos trabajadores', style5)
        ws.write_merge(row + 1 , row + 1, 1, 2, 'Primaria', style5)
        ws.write_merge(row + 1, row + 1, 3, 4, tools.ustr(counter_primary), style5)
        ws.write_merge(row + 2 , row + 2, 1, 2, 'Secundaria Básica', style5)
        ws.write_merge(row + 2, row + 2, 3, 4, tools.ustr(counter_secondary), style5)
        ws.write_merge(row + 3 , row + 3, 1, 2, 'Obrero Calificado', style5)
        ws.write_merge(row + 3, row + 3, 3, 4, tools.ustr(counter_qualify_worker), style5)
        ws.write_merge(row + 4 , row + 4, 1, 2, 'Pre Universitario', style5)
        ws.write_merge(row + 4, row + 4, 3, 4, tools.ustr(counter_pre_university), style5)
        ws.write_merge(row + 5 , row + 5, 1, 2, 'Nivel Medio', style5)
        ws.write_merge(row + 5, row + 5, 3, 4, tools.ustr(counter_middle_level), style5)
        ws.write_merge(row + 6 , row + 6, 1, 2, 'Nivel Superior', style5)
        ws.write_merge(row + 6, row + 6, 3, 4, tools.ustr(counter_high_level), style5)
        ws.write_merge(row + 7 , row + 7, 1, 2, 'Total', style5)
        ws.write_merge(row + 7, row + 7, 3, 4, tools.ustr(counter_all), style5)
        return row

    def get_data(self):
        ws = self.workbook.add_sheet('Employees not in Gforza')
        ws.portrait = 0
        row = 0
        row = self.print_table1(ws, row)
        xls = StringIO()
        self.workbook.save(xls)
        return xls


