# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class production_by_hours(models.Model):
    _name = 'process_control.production_by_hours'

    tecnolog_control_id = fields.Many2one(comodel_name="process_control.tecnolog_control",
                                          string="Modelo Control", ondelete='cascade',
                                          required=True, )

    def _default_hour_production(self):
        return 'Hora extra '

    hour_production = fields.Char(string='Horario', readonly=True, default=_default_hour_production)
    production_count = fields.Float(string='Produccion (Cajones)')

    # @api.model
    # def create(self, vals):
    #     return super(production_by_hours, self).create(vals)

    # @api.onchange('hour_production')
    # def _onchange_hour_production(self):
    #     if not self.hour_production:
    #         pass