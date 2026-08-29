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
        string='Number *', 
        required=True, 
        index=True, 
        help='Number of the phone extension', 
    )
    assign_to = fields.Selection([
        ('job', 'Job'), 
        ('department', 'Department'), 
    ], string='Used By *', required=True, default='job')
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
    )
    state = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ], string='Status *', default='available', tracking=True, required=True)
    
    power_specs = fields.Char(string='Power Specs', help='Ej. "5V 2A", "12V 1A", "PoE 802.3af"')
    state_date = fields.Date('State Date', compute="_compute_state_date", help='Date of last status change')
    calls_cap_plan = fields.Char(string='Calls Cap Plan', help='Contracted calls cap plan')
    calls_code = fields.Char(string='Calls Code', help='Code for calls')
    carrier = fields.Char(string='Carrier', default='ETECSA')
    note = fields.Html(string='Note')
    
    # Domain helper
    employee_domain = fields.Binary(compute='_get_employee_domain', exportable=False)
    show_calls_code_as_password = fields.Boolean(compute="_compute_show_calls_code_as_password")
    

    # ============================================================
    # CONSTRAINS
    # ============================================================
    _sql_constraints = [
        ('unique_number', 'unique(number)', 'Extension number must be unique!'),
        ('unique_calls_code', 'unique(calls_code)', 'Calls code must be unique!'),
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
    def _get_employee_domain(self):
        for ext in self:
            if ext.assign_to == 'job' and ext.job_id:
                ext.employee_domain = [('job_id', '=', ext.job_id.id)]
            elif ext.assign_to == 'department' and ext.department_id:
                ext.employee_domain = [('department_id', '=', ext.department_id.id)]
            else:
                ext.employee_domain = [('id', 'in', [])]

    @api.depends('employee_ids', 'employee_domain')
    def _compute_show_calls_code_as_password(self):
        current_user = self.env.user
        for ext in self:
            # 1. Los managers siempre ven el código (sin puntos)
            if current_user.has_group('ict.group_ict_manager'):
                ext.show_calls_code_as_password = False
                continue

            # 2. Usar el dominio base ya calculado en employee_domain
            domain = list(ext.employee_domain)

            # 3. Obtener los empleados asignados
            if ext.employee_ids:
                domain.append(('id', 'in', ext.employee_ids.employee_id.ids))
            authorized_employees = self.env['hr.employee'].search(domain)

            # 4. Verificar si el usuario actual está vinculado a algún empleado asignado
            if current_user.id in authorized_employees.user_id.ids:
                ext.show_calls_code_as_password = False
            else:
                ext.show_calls_code_as_password = True

    @api.depends('state')
    def _compute_state_date(self):
        for ext in self:
            ext.state_date = fields.Date.today()

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange('assign_to')
    def _onchange_assign_to(self):
        if self.assign_to == 'job':
            self.department_id = False
        elif self.assign_to == 'department':
            self.job_id = False

    @api.onchange('department_id', 'job_id')
    def _onchange_assign(self):
        if self.employee_ids:
            self.employee_ids = [(5, 0, 0)]  # Limpia empleados

    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        if self.employee_ids:
            self.state = 'assigned'
        else:
            self.state = 'available'

    # ============================================================
    # ACTION METHODS
    # ============================================================
    def action_suspend(self):
        self.state = 'suspended'

    def action_activate(self):
        self.state = 'assigned'
    
    def action_cancel(self):
        self.state = 'cancelled'
        # Si estaba asignada, desasignar
        if self.employee_ids:
            self.employee_ids = [(5, 0, 0)]