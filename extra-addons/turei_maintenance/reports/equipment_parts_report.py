# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class EquipmentPartsReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr(lines.category_id.name))
        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        # domain = []
        # if lines.category_id:
        #     domain.append(('equipment_ids.category_id', 'in', lines.category_id.id))

        parts = self.env['turei_maintenance.equipment_parts'].search([])

        worksheet.merge_range('A1:F1', tools.ustr("Control de Piezas x Equipos"), head_format)
        worksheet.merge_range('A2:F2', tools.ustr("Categoría: %s ") % (lines.category_id.name), head_format)

        worksheet.write('A3', tools.ustr('Equipo'), merge_format)
        worksheet.write('B3', tools.ustr('Descripción'), merge_format)
        worksheet.write('C3', tools.ustr('Referencia o Localización'), merge_format)
        worksheet.write('D3', tools.ustr('ITEM'), merge_format)
        worksheet.write('E3', tools.ustr('Código'), merge_format)
        # worksheet.write('F3', tools.ustr('Cantidad'), merge_format)

        x = 3
        for p in parts:
            if p.equipment_ids:
                equip = "\n".join("{} - {}".format(c.name, c.code) for c in p.equipment_ids)
            else:
                equip = ""
            worksheet.write(x, 0, equip, normal_format)
            worksheet.write(x, 1, p.note, normal_format)
            worksheet.write(x, 2, p.reference, normal_format)
            worksheet.write(x, 3, p.item, normal_format)
            worksheet.write(x, 4, p.code, normal_format)
            # worksheet.write(x, 5, p.quantity, normal_format)
            x += 1


EquipmentPartsReport('report.turei_maintenance.equipment_parts_report', 'wzd.equipment.parts')
