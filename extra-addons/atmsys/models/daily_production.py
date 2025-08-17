# -*- coding: utf-8 -*-

from odoo import models, fields


class DailyProduction(models.Model):
    _name = 'atmsys.daily_production'
    _description = 'atmsys.daily_production'
    _rec_name = 'date'

    def _default_get_year(self):
        return fields.Date.from_string(fields.Date.context_today(self)).strftime('%Y')

    date = fields.Date(default=fields.Date.today, required=True)
    year = fields.Char(size=4, required=True, default=_default_get_year)
    destiny_id = fields.Many2one('atmsys.product_destiny', string='Destino', required=True)
    quantity = fields.Float(required=True)
