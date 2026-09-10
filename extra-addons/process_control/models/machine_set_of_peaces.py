# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class MachineSetOfPeaces(models.Model):
    _name = 'process_control.machine_set_of_peaces'
    _description = 'Machine Set Of Peaces'

    name = fields.Char('Name *', required=True)
    machine_type_ids = fields.Many2many(
        comodel_name='process_control.machine_type', 
        relation='process_control_machine_set_of_peaces_machine_type_asoc',
        column1='machine_set_of_peaces_id', 
        column2='machine_type_id', 
        string='Machine Type', 
        ondelete='restrict', 
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name must be unique!'),
    ]