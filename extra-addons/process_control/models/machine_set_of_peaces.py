# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class SetOfPeacesNomenclature(models.Model):
    _name = "process_control.machine_set_of_peaces"
    #_rec_name = "name"
    _description = "Subconjuntos de piezas"

    name = fields.Char('Nombre', size=40, required=True)
    #quantity = fields.Integer(string="Cantidad", required=True, default=1)
    machine_type_ids = fields.Many2many('process_control.machine_type', string='Machine Type', relation="process_control_machine_set_of_peaces_machine_type_asoc",
                                    column1="machine_set_of_peaces_id", column2="machine_type_id", ondelete='restrict'
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El Subconjunto ya existe.'),
    ]