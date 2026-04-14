# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class MachineType(models.Model):
    _name = "process_control_primary.machine_type"
    _description = tools.ustr("Codigo")
    name = fields.Char('Codigo', size=40, required=True)
    equipo = fields.Char('Equipo', size=100, required=True)




