# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

_logger = logging.getLogger(__name__)

class ICTEmployee(models.Model):
    _name = 'ict.employee'
    _description = 'ICT Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    domain_user = fields.Char(string='Username *', required=True, tracking=True)
    domain_id = fields.Many2one(string='Domain', comodel_name='mail.alias.domain', default=lambda self: self.env.company.alias_domain_id.id)
    domain_name = fields.Char(string='Domain Name', related='domain_id.name')
    work_email = fields.Char(string='Email', compute='_compute_work_email', readonly=True)
    hire_date = fields.Date(string='Hire Date', default=fields.Date().today())
    active = fields.Boolean(default=True)
    
    phone_ids = fields.Many2many('ict.phone', 'ict_phone_employee_rel', 'employee_id', 'phone_id', 'Phones')
    computer_ids = fields.Many2many('ict.computer', 'ict_computer_employee_rel', 'employee_id', 'computer_id', 'Computers')

    # Related employee fields
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee *', required=True, tracking=True)
    name = fields.Char(string="Name *", related='employee_id.name')
    user_id = fields.Many2one(related='employee_id.user_id')
    work_phone = fields.Char(related='employee_id.work_phone', readonly=False, related_sudo=False)
    mobile_phone = fields.Char(related='employee_id.mobile_phone', readonly=False, related_sudo=False)
    job_title = fields.Char(related='employee_id.job_title')
    department_id = fields.Many2one(related='employee_id.department_id')
    department_name = fields.Char(string='Department', related='department_id.name')
    
    @api.depends('domain_id', 'domain_user')
    def _compute_work_email(self):
        for employee in self:
            if employee.domain_id and employee.domain_user:
                employee.work_email = employee.domain_user + '@' + employee.domain_id.name
            else:
                employee.work_email = False
            employee.employee_id.work_email = employee.work_email
            # employee.employee_id.sudo().write({
            #     'work_email': employee.work_email
            # })

    @api.constrains('work_email')
    def _check_email(self):
        for record in self:
            if record.work_email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.work_email):
                raise ValidationError("Invalid email format")
