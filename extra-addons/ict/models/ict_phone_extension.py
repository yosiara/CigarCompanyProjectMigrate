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

    number = fields.Char(string='Number', required=True, index=True)
    phone_id = fields.Many2one(
        string='Phone',
        comodel_name='ict.phone',
        ondelete='restrict',
        tracking=True, 
    )
    employee_id = fields.Many2one(
        comodel_name='ict.employee', 
        string='Employee', 
        tracking=True, 
        ondelete='restrict', 
        domain=lambda self: [('job_id', '=', self.job_id.id)] if self.job_id else [('department_id', '=', self.department_id.id)]
    )
    job_id = fields.Many2one(string='Job', comodel_name='hr.job', ondelete='restrict', tracking=True)
    department_id = fields.Many2one(comodel_name='hr.department', string='Department', tracking=True)
    assign_to = fields.Selection([('job', 'Job'), ('department', 'Department')], string='Used By', required=True, default='job')
    notes = fields.Html(string='Notes')

    # ============================================================
    # CONSTRAINS
    # ============================================================
    _sql_constraints = [
        ('unique_number', 'unique(number)', 'Extension number must be unique!'),
    ]

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange("assign_to")
    def _onchange_productive_line_id(self):
        if self.assign_to == 'job':
            self.employee_id = False
            self.department_id = False
        elif self.assign_to == 'department':
            self.employee_id = False
            self.job_id = False