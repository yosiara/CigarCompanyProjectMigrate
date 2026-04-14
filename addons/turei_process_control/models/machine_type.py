# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class MachineType(models.Model):
    _name = "turei_process_control.machine_type"
    _description = tools.ustr("Tipo de Máquina")
    name = fields.Char('Tipo de Máquina', size=40, required=True)
