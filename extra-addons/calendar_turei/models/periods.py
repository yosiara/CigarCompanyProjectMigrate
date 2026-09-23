from odoo import api, fields, models

class Periods(models.Model):
    _name = 'calendar_turei.periods'
    _description = 'Periods'

    name = fields.Char(string='Name *', required=True)
    start_date = fields.Date(string='Start Date *', required=True)
    end_date = fields.Date(string='End Date *', required=True)
    anual = fields.Boolean(string='Represents a Year')