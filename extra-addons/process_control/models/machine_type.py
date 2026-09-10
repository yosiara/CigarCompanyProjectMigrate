# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class MachineType(models.Model):
    _name = 'process_control.machine_type'
    _description = 'Machine Type'
    
    name = fields.Char('Name *', size=40, required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This type of machine already exists!'),
    ]
