# -*- coding: utf-8 -*-


from odoo import models, fields, api


class InterruptionType(models.Model):
    _name = 'turei_process_control.interruption.type'

    name = fields.Char(string="Nombre", required=True, )
    machines_related = fields.Many2many(comodel_name="turei_process_control.machine_type",
                                        relation="turei_process_control_interruption_machine_asoc",
                                        column1="int_type_id",
                                        column2="machine_id", string="Máquinas asociadas", )
    use_in_any_machine = fields.Boolean(string="Usar para cualquier máquina", default=False)
    is_linked_to_machine = fields.Boolean(string="Vinculada a máquina", default=False)
    cause = fields.Selection(string="Causa",
                             selection=[('endogena', 'ENDÓGENAS (Internas)'), ('exogena', 'EXÓGENAS (Externas)'), ],
                             required=True, default='endogena')
    code = fields.Char(string="Código", )
