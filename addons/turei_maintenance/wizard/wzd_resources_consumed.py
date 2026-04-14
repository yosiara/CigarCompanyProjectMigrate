# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdResourcesConsumed(models.TransientModel):
    _name = 'wzd.resources.consumed'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipo', domain="[('is_industrial', '=', True)]")
    category_id = fields.Many2one('maintenance.equipment.category', string='Taller')

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_maintenance.resources_consumed_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'equipment_id': self.equipment_id.id,
            'category_id': self.category_id.id,
        })

