# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Char, Text, Date, Many2one, Integer

class Area(Model):
    _name = 'l10n_cu_base.area'
    _description = 'l10n_cu_base.area'

    code = Char(required=True)
    name = Char(required=True)
    abbreviation = Char()
    color = Integer()
Area()
