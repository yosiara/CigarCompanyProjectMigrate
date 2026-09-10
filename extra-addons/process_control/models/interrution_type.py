# -*- coding: utf-8 -*-
from odoo import models, fields, api

class InterruptionType(models.Model):
    _name = 'process_control.interruption_type'
    _description = 'Interruption Type'

    name = fields.Char(string='Name *', required=True)
    code = fields.Char(string='Code')
    activate = fields.Boolean(string='Active', default=True)
    machine_type_related = fields.Many2many(
        comodel_name='process_control.machine_type', 
        relation='process_control_interruption_type_machine_type_asoc',
        column1='interruption_type_id', 
        column2='machine_type_id', 
        string='Machine Type',
    )
    cause = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], string='Cause *', default='internal', required=True)
    