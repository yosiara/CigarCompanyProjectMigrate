# -*- coding: utf-8 -*-


from odoo import models, fields, api


class InterruptionType(models.Model):
    _name = 'process_control_primary.interruption.type'

    name = fields.Char(string="Nombre", required=True, )
    line_related = fields.Many2many(comodel_name="process_control_primary.productive_line",
                                        relation="process_control_primary_interruption_productive_line_asoc",
                                        column1="int_type_id",
                                        column2="productive_line_id", string="Linea asociada", )

    is_linked_to_machine = fields.Boolean(string="Vinculada a máquina", default=False)
    use_in_any = fields.Boolean(string="Usar para cualquiera", default=False)
    cause = fields.Selection(string="Causa",
                             selection=[('endogena', 'ENDÓGENAS (Internas)'), ('exogena', 'EXÓGENAS (Externas)'), ],
                             required=True, default='endogena')
