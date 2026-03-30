from odoo import api, fields, models

class Periods(models.Model):
    _name = 'calendar_turei.periods'
    _description = 'calendar_turei.periods'

    name = fields.Char(string='Nombre', required=True)
    date_start = fields.Date(string='Inicio', required=True)
    date_end = fields.Date(string='Fin', required=True)
    anual = fields.Boolean(string='Representa Año')