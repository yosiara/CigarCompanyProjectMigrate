# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Char, Text, Many2one


class CostCenter(Model):
    _name = 'base_cu.cost_center'
    _description = 'base_cu.cost_center'

    code = Char(required=True)
    name = Char(required=True)
    note = Text(string='Description')
    responsibility_area_id = Many2one('base_cu.responsibility_area', string='Responsibility Area')

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The code must be unique!'),
    ]
CostCenter()
