# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ICTPhone(models.Model):
    _name = 'ict.phone'
    _description = 'ICT Phone'
    
    name = fields.Char(string='Serial Number/IMEI', required=True)
    brand = fields.Char(string='Brand', required=True)
    model = fields.Char(string='Model', required=True)
    phone_number = fields.Char(string='Phone Number', required=True)
    carrier = fields.Selection([
        ('movistar', 'Movistar'),
        ('claro', 'Claro'),
        ('personal', 'Personal'),
        ('tuenti', 'Tuenti'),
    ], string='Carrier')
    
    employee_ids = fields.Many2many('ict.employee', 'ict_phone_employee_rel', 'phone_id', 'employee_id', 'Employees')
    data_plan = fields.Boolean(string='Includes Data Plan')
    data_gb = fields.Integer(string='Data GB')
    
    assignment_date = fields.Date(string='Assignment Date')
    state = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('repair', 'Under Repair'),
        ('retired', 'Retired'),
    ], string='Status', default='available')
    
    active = fields.Boolean(default=True)

