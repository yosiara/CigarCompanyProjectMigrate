# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

_logger = logging.getLogger(__name__)

class ICTEmployee(models.Model):
    _name = 'ict.employee'
    _description = 'Domain Employees'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(comodel_name='hr.employee', string='ICT Employee', required=True, tracking=True)
    name = fields.Char(string='Name', related='employee_id.name')
    department_id = fields.Many2one(string='Department', related='employee_id.department_id')
    user_id = fields.Many2one(related='employee_id.user_id')
    work_email = fields.Char(related='employee_id.work_email', readonly=False, related_sudo=False)
    work_phone = fields.Char(related='employee_id.work_phone', readonly=False, related_sudo=False)
    mobile_phone = fields.Char(related='employee_id.mobile_phone', readonly=False, related_sudo=False)
    
    domain = fields.Char(string='Domain', required=True, tracking=True)
    domain_user = fields.Char(string='Domain Username', required=True, tracking=True)
    position = fields.Char(string='Position')
    hire_date = fields.Date(string='Hire Date')
    active = fields.Boolean(default=True)
    
    # Relations
    computer_ids = fields.One2many('ict.computer', 'employee_ids', string='Assigned Computers')
    # phone_ids = fields.One2many('ict.phone', 'employee_id', string='Assigned Phones')
    
    @api.depends('domain', 'domain_user')
    def _compute_email(self):
        for employee in self:
            if employee.domain and employee.domain_user:
                employee.work_email = employee.domain_user + '@' + employee.domain

    @api.constrains('work_email')
    def _check_email(self):
        for record in self:
            if record.work_email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.work_email):
                raise ValidationError("Invalid email format")