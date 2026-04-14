# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Area(models.Model):
    _name = 'base_cu.area'
    _description = 'base_cu.area'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    abbreviation = fields.Char('Abbreviation')
    color = fields.Integer('Color')