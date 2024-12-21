# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class MachinePiaces(models.Model):
    _name = "process_control.machine_peaces"
    _description = "Peaces"

    set_of_peaces_id = fields.Many2one('process_control.machine_set_of_peaces', string='Subset')
    machine_id = fields.Many2one('process_control.machine', string='Machine')
    name = fields.Char(related='set_of_peaces_id.name', required=True)
    quantity = fields.Integer(string="Cantidad", required=True, default=1)