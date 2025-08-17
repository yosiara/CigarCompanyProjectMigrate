# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdResourcesConsumed(models.TransientModel):
    _name = 'wzd.request.maint'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    category_id = fields.Many2one('maintenance.equipment.category', string='Taller')
    maintenance_team_id = fields.Many2one('maintenance.team', string='Brigada de Mantenimiento')

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_maintenance.request_maint_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'category_id': self.category_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
        })

