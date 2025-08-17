# -*- coding: utf-8 -*-


from odoo import models, fields, tools
from datetime import timedelta, datetime


class WzdPlanMtto(models.TransientModel):
    _name = 'wzd.plan.mtto'

    date = datetime.today().date()
    current_year = date.year
    new_year = date.replace(year=current_year + 1).year

    year = fields.Selection(string="Año", selection=[('current', tools.ustr(current_year)), ('new', tools.ustr(new_year))], required=True, default='current')
    category_id = fields.Many2one('maintenance.equipment.category', string='Taller')
    maintenance_team_id = fields.Many2one('maintenance.team', string='Brigada de Mantenimiento')

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_maintenance.plan_mtto_report', data={
            'year': self.year,
            'category_id': self.category_id.id,
            'maintenance_team_id': self.maintenance_team_id.id
        })

