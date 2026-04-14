# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CostCenter(models.Model):
    _name = 'base_cu.cost_center'
    _description = 'Cost Center'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    note = fields.Text(string='Description')
    responsibility_area_id = fields.Many2one('base_cu.responsibility_area', string='Responsibility Area')

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The code must be unique!'),
    ]