# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Char, One2many


class ResponsibilityArea(Model):
    _name = 'base_cu.responsibility_area'
    _description = 'base_cu.responsibility_area'

    code = Char(required=True)
    name = Char(required=True)
    cost_center_ids = One2many('base_cu.cost_center', 'responsibility_area_id', 'Cost Centers')

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The code must be unique!'),
    ]
ResponsibilityArea()
