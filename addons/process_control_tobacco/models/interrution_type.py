# -*- coding: utf-8 -*-


from odoo import models, fields, api


class InterruptionType(models.Model):
    _name = 'process_control_tobacco.interruption.type'

    name = fields.Char(string="Nombre", required=True, )
    code = fields.Char('Codigo', size=40, required=True)

    is_linked_to_machine = fields.Boolean(string="Vinculada a máquina", default=False)
    use_in_any = fields.Boolean(string="Usar para cualquiera", default=False)
    cause = fields.Selection(string="Causa",
                             selection=[('endogena', 'ENDÓGENAS (Internas)'), ('exogena', 'EXÓGENAS (Externas)'), ],
                             required=True, default='endogena')
