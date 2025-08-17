# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Char, Text, Date, Many2one, Integer

class Area(Model):
    _name = 'base_cu.area'
    _description = 'base_cu.area'

    code = Char(required=True)
    name = Char(required=True)
    abbreviation = Char()
    color = Integer()
Area()
