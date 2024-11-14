# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class SetOfPeacesNomenclature(models.Model):
    _name = "process_control.machine_set_of_peaces_nomenclature"
    _rec_name = "name"
    _description = "Nombres de conjunto de piezas"

    name = fields.Char('Nombre del conjunto', size=40, required=True)
    machine_type_id = fields.Many2one('process_control.machine_type', string='Tipo de máquina')