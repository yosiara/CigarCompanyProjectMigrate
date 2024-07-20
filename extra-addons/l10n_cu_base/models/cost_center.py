# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Char, Text, Many2one


class CostCenter(Model):
    _name = 'l10n_cu_base.cost_center'
    _description = 'l10n_cu_base.cost_center'

    code = Char(required=True)
    name = Char(required=True)
    note = Text(string='Description')
    responsibility_area_id = Many2one('l10n_cu_base.responsibility_area', string='Responsibility Area')

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The code must be unique!'),
    ]
CostCenter()
