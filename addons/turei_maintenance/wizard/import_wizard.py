# -*- coding: utf-8 -*-

import base64
import logging
import os
import datetime
import xlrd
import tempfile

from os.path import normpath, abspath
from odoo.fields import Selection, Binary, Char
from odoo.models import TransientModel
from odoo.tools import ustr
from odoo.modules.module import get_module_path

_logger = logging.getLogger('INFO')


class ImportWizard(TransientModel):
    _name = 'turei_maintenance.import_wizard'
    _description = 'turei_maintenance.import_wizard'

    filename = Char()
    file = Binary(string='File', required=True)
    action = Selection([('import_cycle_maintenance', 'Importar Ciclos de Mantenimientos x Equipos'),
                        ('import_date_cycle', 'Importar Ciclo y Fecha de Inicio para Plan'),
                        ('import_line', 'Importar Líneas a los Equipos'),
                        ('import_electric_motor', 'Importar Motores Electricos')], string='Importar')

    def action_import(self):
        if self.action in ['import_cycle_maintenance']:
            return self.action_import_cycle_maintenance()
        if self.action in ['import_date_cycle']:
            return self.import_date_cycle()
        if self.action in ['import_line']:
            return self.import_line()
        if self.action in ['import_electric_motor']:
            return self.import_electric_motor()

    def action_import_cycle_maintenance(self):
        path = self._save_file()
        doc = xlrd.open_workbook(path)
        sheet = doc.sheet_by_index(0)

        equipment_obj = self.env['maintenance.equipment']
        cycle_maintenance_obj = self.env['turei_maintenance.cycle_maintenance']

        x = 0

        while x < sheet.nrows:
            try:
                code = ustr(sheet.cell_value(x, 0))
            except Exception as e:
                code = False
            try:
                cycle = sheet.cell_value(x, 2)
            except Exception as e:
                cycle = False

            if code:
                equipment = equipment_obj.search([('code', '=', code)])
            if cycle:
                arr_cycle = cycle.split('-')

            if code and len(arr_cycle) > 0:
                for c in arr_cycle:
                    if equipment:
                        cycle_maintenance_id = cycle_maintenance_obj.create({'cycle': c})
                        equipment.write({'cycle_maintenance_ids': [(4, cycle_maintenance_id.id, 0)]})

            x += 1

        os.remove(path)

    def import_date_cycle(self):
        path = self._save_file()
        doc = xlrd.open_workbook(path)
        sheet = doc.sheet_by_index(0)

        equipment_obj = self.env['maintenance.equipment']
        cycle_maintenance_obj = self.env['turei_maintenance.cycle_maintenance']

        x = 1
        while x < sheet.nrows:
            try:
                code = sheet.cell_value(x, 0)
            except Exception as e:
                code = False
            try:
                cycle = sheet.cell_value(x, 1)
            except Exception as e:
                cycle = False
            try:
                date = datetime.datetime(*xlrd.xldate_as_tuple(sheet.cell_value(x, 2),doc.datemode))
            except Exception as e:
                date = False
            if code:
                equipment = equipment_obj.search([('code', '=', code)])
            if cycle and equipment:
                date_cycle_id = cycle_maintenance_obj.search([('cycle', '=', cycle), ('equipment_id', '=', equipment.id)]).id
            if date and date_cycle_id:
                equipment.write({'config_date': date, 'config_cycle': date_cycle_id})
            x += 1

    def import_line(self):
        path = self._save_file()
        doc = xlrd.open_workbook(path)
        sheet = doc.sheet_by_index(0)

        equipment_obj = self.env['maintenance.equipment']
        linea_obj = self.env['turei_maintenance.line']
        x = 0
        while x < sheet.nrows:
            try:
                code = sheet.cell_value(x, 0)
            except Exception as e:
                code = False
            try:
                linea = sheet.cell_value(x, 1)
            except Exception as e:
                linea = False

            if linea:
                linea_id = linea_obj.search([('name', '=', linea)]).id

            if code and linea_id:
                equipment = equipment_obj.search([('code', '=', code)])
                equipment.write({'line_id': linea_id})
            x += 1

    def import_electric_motor(self):
        path = self._save_file()
        doc = xlrd.open_workbook(path)
        sheet = doc.sheet_by_index(0)

        electric_motor_obj = self.env['turei_maintenance.equipment_electric_motor']

        x = 1
        while x < sheet.nrows:
            vals = {
                'brand': sheet.cell_value(x, 0) if sheet.cell_value(x, 0) else False,
                'model': sheet.cell_value(x, 1) if sheet.cell_value(x, 1) else False,
                'fabricator': sheet.cell_value(x, 2) if sheet.cell_value(x, 2) else False,
                'serial_no': sheet.cell_value(x, 3) if sheet.cell_value(x, 3) else False,
                'no_motor': sheet.cell_value(x, 4) if sheet.cell_value(x, 4) else False,
                'review_frequency': sheet.cell_value(x, 5) if sheet.cell_value(x, 5) else False,
                'clase': sheet.cell_value(x, 6) if sheet.cell_value(x, 6) else False,
                'service': sheet.cell_value(x, 7) if sheet.cell_value(x, 7) else False,
                'quantity': sheet.cell_value(x, 8) if sheet.cell_value(x, 8) else False,
                'hp': sheet.cell_value(x, 9) if sheet.cell_value(x, 9) else False,
                'kw': float(sheet.cell_value(x, 10)) if sheet.cell_value(x, 10) else False,
                'volts': sheet.cell_value(x, 11) if sheet.cell_value(x, 11) else False,
                'cycles': int(sheet.cell_value(x, 12)) if sheet.cell_value(x, 12) else False,
                'amps': sheet.cell_value(x, 13) if sheet.cell_value(x, 13) else False,
                'phase': int(sheet.cell_value(x, 14)) if sheet.cell_value(x, 14) else False,
                'rpm': sheet.cell_value(x, 15) if sheet.cell_value(x, 15) else False,
                'pulley_side': sheet.cell_value(x, 16) if sheet.cell_value(x, 16) else False,
                'cap_side': sheet.cell_value(x, 17) if sheet.cell_value(x, 17) else False,
                'subset': sheet.cell_value(x, 18) if sheet.cell_value(x, 18) else False
            }
            print(vals)
            electric_motor_obj.create(vals)
            x += 1



    def _save_file(self):
        # path = get_module_path('turei_maintenance')
        # path += '/static/upload/' + self.filename
        # path = normpath(path)
        #
        # f = open(path, "wb")
        # f.write(base64.b64decode(self.file))
        # f.close()
        file_path = tempfile.gettempdir() + '/file.xlsx'
        path = normpath(file_path)
        data = self.file
        f = open(path, 'wb')
        f.write(base64.decodestring(data))
        f.close()

        return abspath(path)

