# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Integer


class Warehouse(Model):
    _inherit = 'warehouse.warehouse'
    
    external_id = Integer()

    _sql_constraints = [
        ('unique_external_id', 'unique(external_id)', 'The external identifier must be unique!'),
    ]
Warehouse()