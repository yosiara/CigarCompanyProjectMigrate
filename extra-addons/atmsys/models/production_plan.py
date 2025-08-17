# -*- coding: utf-8 -*-

from odoo import models, fields


class AnnualServicePlan(models.Model):
    _name = 'atmsys.production_plan'
    _description = 'atmsys.production_plan'
    _rec_name = 'year'

    def _default_get_year(self):
        return fields.Date.from_string(fields.Date.context_today(self)).strftime('%Y')

    year = fields.Char(size=4, required=True, default=_default_get_year)
    record_ids = fields.One2many('atmsys.plan_record', inverse_name='plan_id', string='Planes')


class AnnualServicePlanRecord(models.Model):
    _name = 'atmsys.plan_record'
    _description = 'atmsys.plan_record'

    plan_id = fields.Many2one('atmsys.production_plan', string='Plan')
    destiny_id = fields.Many2one('atmsys.product_destiny', string='Destino')

    plan01 = fields.Float(string='Enero')
    plan02 = fields.Float(string='Febrero')
    plan03 = fields.Float(string='Marzo')
    plan04 = fields.Float(string='Abril')
    plan05 = fields.Float(string='Mayo')
    plan06 = fields.Float(string='Junio')
    plan07 = fields.Float(string='Julio')
    plan08 = fields.Float(string='Agosto')
    plan09 = fields.Float(string='Septiembre')
    plan10 = fields.Float(string='Octubre')
    plan11 = fields.Float(string='Noviembre')
    plan12 = fields.Float(string='Diciembre')
