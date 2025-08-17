# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class ResponsibilityArea(models.Model):
    _name = 'base_cu.responsibility_area'
    _description = 'Responsibility Area'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    cost_center_ids = fields.One2many('base_cu.cost_center', 'responsibility_area_id', 'Cost Centers')

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The code must be unique!'),
    ]