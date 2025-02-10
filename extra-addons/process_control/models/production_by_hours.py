# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class ProductionByHours(models.Model):
    _name = 'process_control.production_by_hours'
    _description = "Production By Hours"

    hour_production = fields.Char(string='Horario', readonly=True, default="Hora extra ")
    production_count = fields.Float(string='Produccion (Cajones)')

    tecnolog_control_id = fields.Many2one(comodel_name="process_control.tecnolog_control", string="Modelo Control", ondelete='cascade', required=True)
    
    # @api.model
    # def create(self, vals):
    #     return super(production_by_hours, self).create(vals)

    # @api.onchange('hour_production')
    # def _onchange_hour_production(self):
    #     if not self.hour_production:
    #         pass