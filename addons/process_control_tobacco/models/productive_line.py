# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ProductiveLine(models.Model):
    _name = "process_control_tobacco.productive_line"
    _description = tools.ustr("Línea Productiva")
    _order = 'name'
    _rec_name = 'name'

    def _get_default_name(self):
        return 'Línea '

    name = fields.Char('Nombre', size=40, required=True, copy=False, default=_get_default_name)
    codigo = fields.Char('Codigo')
    machine_type_ids = fields.Many2many('process_control_tobacco.machine_type',
                                   relation="process_control_tobacco_produc_line_machine_type_asoc",
                                   column1="prod_line_id", copy=False,
                                   column2="machine_type_id", string='Máquinas')


    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'El nombre de la línea productiva debe ser único.'),
    ]



