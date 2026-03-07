# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

_logger = logging.getLogger(__name__)

class ITEmployee(models.Model):
    _name = 'it.employee'
    _description = 'Domain Employees'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Full Name', required=True, tracking=True)
    domain_user = fields.Char(string='Domain Username', required=True, tracking=True)
    email = fields.Char(string='Corporate Email', required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    phone = fields.Char(string='Mobile Phone')
    phone_extension = fields.Char(string='Extension')
    position = fields.Char(string='Position')
    hire_date = fields.Date(string='Hire Date')
    active = fields.Boolean(default=True)
    
    # Relations
    computer_ids = fields.One2many('it.computer', 'employee_id', string='Assigned Computers')
    phone_ids = fields.One2many('it.phone', 'employee_id', string='Assigned Phones')
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                raise ValidationError("Invalid email format")