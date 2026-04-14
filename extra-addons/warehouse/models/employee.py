# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models

class Employee(models.Model):
    _inherit = 'hr.employee'

    can_authorize_a_request = fields.Boolean(string='Can authorize a request?')