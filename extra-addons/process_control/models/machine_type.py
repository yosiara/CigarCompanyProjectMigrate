# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class MachineType(models.Model):
    _name = "process_control.machine_type"
    _description = "Tipo de Máquina"
    
    name = fields.Char('Tipo de Máquina', size=40, required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'EL tipo de máquina ya existe.'),
    ]
