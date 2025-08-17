# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools



class Line(models.Model):
    _name = 'turei_maintenance.line'

    name = fields.Char(required=True, string='Nombre')
    sequence = fields.Integer(string='Secuencia')
    is_start = fields.Boolean(string='Es la Línea Inicial?')
    is_end = fields.Boolean(string='Es la Línea Final?')
    is_module = fields.Boolean(string='Es módulo?')
    special_regime = fields.Boolean(string="Régimen Especial?")
    taller = fields.Many2one('maintenance.equipment.category', string='Taller')
    is_secundary = fields.Boolean(related="taller.is_secundary")



