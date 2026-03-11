# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ICTService(models.Model):
    _name = 'ict.service'
    _description = 'ICT Services'
    
    name = fields.Char(string='Service Name', required=True)
    type = fields.Selection([
        ('internet', 'Internet'),
        ('telephony', 'Telephony'),
        ('cloud', 'Cloud Services'),
        ('software', 'Software Licenses'),
        ('support', 'Technical Support'),
    ], string='Service Type', required=True)
    
    supplier = fields.Char(string='Supplier')
    monthly_cost = fields.Float(string='Monthly Cost')
    contract_date = fields.Date(string='Contract Date')
    renewal_date = fields.Date(string='Renewal Date')
    
    department_ids = fields.Many2many('hr.department', string='Benefited Departments')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

