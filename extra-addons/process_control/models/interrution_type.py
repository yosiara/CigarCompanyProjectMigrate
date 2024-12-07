# -*- coding: utf-8 -*-


from odoo import models, fields, api


class InterruptionType(models.Model):
    _name = "process_control.interruption_type"
    _description = "Interruption Type"

    name = fields.Char(string="Nombre *", required=True)
    machine_type_related = fields.Many2many(comodel_name="process_control.machine_type",
                                        relation="process_control_interruption_type_machine_type_asoc",
                                        column1="interruption_type_id",
                                        column2="machine_type_id", string="Tipo de Máquinas")
    #use_in_any_machine = fields.Boolean(string="Usar para cualquier máquina", default=False)
    activate = fields.Boolean(string="Activa", default=True)
    cause = fields.Selection(string="Causa *", required=True, default='endogena', selection=[
        ('endogena', 'ENDÓGENAS (Internas)'),
        ('exogena', 'EXÓGENAS (Externas)')
    ])
    code = fields.Char(string="Código")