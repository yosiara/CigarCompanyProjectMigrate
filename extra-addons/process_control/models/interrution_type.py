# -*- coding: utf-8 -*-
from odoo import models, fields, api

class InterruptionType(models.Model):
    _name = "process_control.interruption_type"
    _description = "Interruption Type"

    name = fields.Char(string="Nombre *", required=True)
    
    code = fields.Char(string="Código")

    activate = fields.Boolean(string="Activa", default=True)
    
    cause = fields.Selection(string="Causa *", selection=[
        ('endogena', 'Endógenas (Internas)'),
        ('exogena', 'Exógenas (Externas)'),
    ], default='endogena', required=True)
    
    machine_type_related = fields.Many2many(comodel_name="process_control.machine_type", string="Tipos de Máquinas",
                                        relation="process_control_interruption_type_machine_type_asoc",
                                        column1="interruption_type_id", column2="machine_type_id")
    