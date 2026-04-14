# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class MachineSetOfPeaces(models.Model):
    _name = "process_control.machine_set_of_peaces"
    _description = "Machine Set Of Peaces"
    #_rec_name = "name"

    name = fields.Char('Nombre *', required=True)
    #quantity = fields.Integer(string="Cantidad", required=True, default=1)
    machine_type_ids = fields.Many2many('process_control.machine_type', string='Tipos de Máquina', relation="process_control_machine_set_of_peaces_machine_type_asoc",
                                    column1="machine_set_of_peaces_id", column2="machine_type_id", ondelete='restrict'
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El Subconjunto ya existe.'),
    ]