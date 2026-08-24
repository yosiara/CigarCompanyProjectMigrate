# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ICTPhoneExtension(models.Model):
    _name = 'ict.phone.extension'
    _description = 'ICT Phone Extension'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'

    number = fields.Char(
        string='Number', 
        required=True, 
        index=True, 
        help='Number of the phone extension', 
    )
    assign_to = fields.Selection([
        ('job', 'Job'), 
        ('department', 'Department'), 
    ], string='Used By', required=True, default='job')
    assign_date = fields.Date('Assigned Date', tracking=True, compute="_compute_assign_date")
    job_id = fields.Many2one(
        string='Job', 
        comodel_name='hr.job', 
        ondelete='restrict', 
        tracking=True, 
    )
    department_id = fields.Many2one(
        string='Department', 
        comodel_name='hr.department', 
        ondelete='restrict', 
        tracking=True, 
    )
    phone_id = fields.Many2one(
        string='Phone',
        comodel_name='ict.phone',
        ondelete='restrict',
        tracking=True, 
    )
    employee_ids = fields.Many2many(
        'ict.employee',
        'ict_extension_employee_rel',
        'extension_id',
        'employee_id',
        string='Employees',
        tracking=True,
        domain=lambda self: [('job_id', '=', self.job_id.id)] if self.job_id else [('department_id', '=', self.department_id.id)], 
    )
    state = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ], string='Status *', default='available', tracking=True, required=True)
    notes = fields.Html(string='Notes')
    
    # Domain helper
    allowed_employee_ids = fields.Many2many(
        'ict.employee',
        compute='_compute_allowed_employees',
        store=False,
    )

    # ============================================================
    # CONSTRAINS
    # ============================================================
    _sql_constraints = [
        ('unique_number', 'unique(number)', 'Extension number must be unique!'),
    ]

    @api.constrains('employee_ids', 'job_id', 'department_id', 'assign_to')
    def _check_assignment(self):
        for rec in self:
            if rec.assign_to == 'job':
                if not rec.job_id:
                    raise ValidationError(_("The 'Job' field is required when 'Used By' is 'Job'."))
                if rec.employee_ids:
                    invalid = rec.employee_ids.filtered(lambda e: e.job_id != rec.job_id)
                    if invalid:
                        raise ValidationError(_("Employees %s do not belong to this job") % invalid.mapped('name'))
            elif rec.assign_to == 'department':
                if not rec.department_id:
                    raise ValidationError(_("The 'Department' field is required when 'Used By' is 'Department'."))
                if rec.employee_ids:
                    invalid = rec.employee_ids.filtered(lambda e: e.department_id != rec.department_id)
                    if invalid:
                        raise ValidationError(_("Employees %s do not belong to this department") % invalid.mapped('name'))

    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    @api.depends('job_id', 'department_id', 'assign_to')
    def _compute_allowed_employees(self):
        for rec in self:
            employees = self.env['ict.employee']
            if rec.assign_to == 'job' and rec.job_id:
                employees = rec.job_id.employee_ids
            elif rec.assign_to == 'department' and rec.department_id:
                employees = rec.department_id.member_ids
            rec.allowed_employee_ids = [(6, 0, employees.ids)]

    @api.depends('job_id', 'department_id')
    def _compute_assign_date(self):
        for ext in self:
            if (ext.assign_to == 'job' and ext.job_id) or (ext.assign_to == 'department' and ext.department_id):
                ext.assign_date = fields.Date.today()
            else:
                ext.assign_date = False

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange('assign_to')
    def _onchange_assign_to(self):
        if self.assign_to == 'job':
            self.department_id = False
        elif self.assign_to == 'department':
            self.job_id = False
        self.employee_ids = [(5, 0, 0)]  # Limpia empleados