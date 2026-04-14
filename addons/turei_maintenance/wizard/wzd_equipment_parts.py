# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdEquipmentParts(models.TransientModel):
    _name = 'wzd.equipment.parts'

    category_id = fields.Many2one('maintenance.equipment.category', string='Categoría')

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_maintenance.equipment_parts_report', data={
            'category_id': self.category_id.id
        })

