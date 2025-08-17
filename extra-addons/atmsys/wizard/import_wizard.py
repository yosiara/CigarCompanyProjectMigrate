# -*- coding: utf-8 -*-

import base64
import logging
import os
from os.path import normpath, abspath

import xlrd
from odoo.fields import Selection, Binary, Char
from odoo.models import TransientModel
from odoo.tools import ustr
from odoo.modules.module import get_module_path

_logger = logging.getLogger('INFO')


class ImportWizard(TransientModel):
    _name = 'atmsys.import_wizard'
    _description = 'atmsys.import_wizard'

    filename = Char()
    file = Binary(string='File', required=True)
    action = Selection([('import_responsibility_areas', 'Import Responsibility Areas...'),
                        ('import_cost_centers', 'Import Cost Centers...'),
                        ('import_product_groups', 'Import Product Groups')], string='Import')

    def action_import(self):
        #product_control_obj = self.env['warehouse.product_control']
        #prod_controls = product_control_obj.search([('quantity', '<', 0.0)])
        #for control in prod_controls:
        #    control.write({'quantity': -control.quantity})
        #return True
        
        
        #
        # request_obj = self.env['warehouse.warehouse_request']
        # requests = request_obj.search([])
        #
        # for request in requests:
        #     for requested_product in request.requested_product_ids:
        #         controls = product_control_obj.search([
        #             ('warehouse_id', '=', requested_product.warehouse_id.id),
        #             ('product_id', '=', requested_product.product_id.id)
        #         ])
        #
        #         if len(controls):
        #             cant = controls[0].quantity_system - requested_product.quantity
        #             controls.write({'quantity_system': cant})
        #
        # return True

        # x = 1
        # _vals = {
        #     'quantity_system': 0.0,
        #     'quantity': 0.0,
        # }
        #
        # for cont in xlist:
        #     cont.write(_vals)
        #
        #     _logger.info("updated product control: %s." % (str(x),))
        #     x += 1
        # return True
        #
        # mov_obj = self.env['versat_integration.product_movement']
        # movements = mov_obj.search([('description', '=', 'Almacén 2-Vale de Salida')])
        #
        # x = 0
        # for mov in movements:
        #     mov.unlink()
        #     _logger.info("deleted movement: %s." % (str(x),))
        #     x += 1
        #
        # return True

        if self.action in ['import_responsibility_areas']:
            return self.action_import_responsibility_areas()
        elif self.action in ['import_cost_centers']:
            return self.action_import_cost_centers()
        elif self.action in ['import_product_groups']:
            return self.action_import_product_groups()

    def action_import_responsibility_areas(self):
        path = self._save_file()
        doc = xlrd.open_workbook(path)
        sheet = doc.sheet_by_index(0)

        area_obj = self.env['l10n_cu_base.responsibility_area']
        x = 1

        while x < sheet.nrows:
            try:
                code = sheet.cell_value(x, 0)
            except Exception as e:
                code = False

            try:
                name = ustr(sheet.cell_value(x, 1))
            except Exception as e:
                name = ''

            if code:
                areas = area_obj.search([('code', '=', code)])
                x += 1

                if not len(areas):
                    area_obj.create({'code': code, 'name': name})
                else:
                    areas.write({'name': name})

        os.remove(path)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('atmsys.atmsys_responsibility_area_menu_item').id},
        }

    def action_import_cost_centers(self):
        path = self._save_file()
        doc = xlrd.open_workbook(path)
        sheet = doc.sheet_by_index(0)

        area_obj = self.env['l10n_cu_base.responsibility_area']
        cost_center_obj = self.env['l10n_cu_base.cost_center']
        x = 1

        while x < sheet.nrows:
            try:
                code_area = sheet.cell_value(x, 0)
            except Exception as e:
                code_area = False

            try:
                code = sheet.cell_value(x, 1)
            except Exception as e:
                code = False

            try:
                name = ustr(sheet.cell_value(x, 2))
            except Exception as e:
                name = ''

            try:
                note = sheet.cell_value(x, 3)
            except Exception as e:
                note = ''

            if code:
                areas = area_obj.search([('code', '=', code_area)])
                cost_centers = cost_center_obj.search([('code', '=', code)])
                area_id = areas[0].id if len(areas) else False
                x += 1

                if not len(cost_centers):
                    cost_center_obj.create({'code': code, 'name': name, 'note': note, 'responsibility_area_id': area_id})
                else:
                    cost_center_obj.write({'name': name, 'note': note, 'responsibility_area_id': area_id})

        os.remove(path)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('atmsys.atmsys_cost_enter_menu_item').id},
        }

    def action_import_product_groups(self):
        path = self._save_file()
        doc = xlrd.open_workbook(path)
        sheet = doc.sheet_by_index(0)

        group_obj = self.env['simple_product.product.group']
        x = 1

        while x < sheet.nrows:
            try:
                code = sheet.cell_value(x, 0)
            except Exception as e:
                code = False

            try:
                name = ustr(sheet.cell_value(x, 1))
            except Exception as e:
                name = ''

            try:
                notes = ustr(sheet.cell_value(x, 2))
            except Exception as e:
                notes = ''

            if code:
                groups = group_obj.search([('code', '=', code)])
                x += 1

                if not len(groups):
                    group_obj.create({'code': code, 'name': name, 'description': notes})
                else:
                    groups.write({'name': name, 'description': notes})

        os.remove(path)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('simple_product.simple_product_product_group_root_menu').id},
        }

    def _save_file(self):
        path = get_module_path('atmsys')
        path += '/static/upload/' + self.filename
        path = normpath(path)

        f = open (path, "wb")
        f.write(base64.b64decode(self.file))
        f.close()

        return abspath(path)
ImportWizard()
