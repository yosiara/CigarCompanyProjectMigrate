# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ICTMobileLine(models.Model):
    _name = 'ict.mobile.line'
    _description = 'ICT Mobile Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'
    
    number = fields.Char(
        string='Number *',
        required=True,
        index=True,
        help='Number of the line'
    )
    job_id = fields.Many2one(
        string='Job *', 
        comodel_name='hr.job', 
        ondelete='restrict', 
        tracking=True, 
        required=True, 
    )
    mobile_id = fields.Many2one(
        string='Mobile',
        comodel_name='ict.mobile',
        ondelete='restrict',
        tracking=True, 
    )
    employee_ids = fields.Many2many(
        'ict.employee',
        'ict_line_employee_rel',
        'line_id',
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

    state_date = fields.Date('State Date', tracking=True, compute="_compute_state_date", help='Date of last status change')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    carrier = fields.Char(string='Carrier', default='ETECSA')

    # ETECSA data
    imsi = fields.Char(string='IMSI', help='International Mobile Subscriber Identity')
    sim_card = fields.Char(string='SIM Card', help='SIM card serial number (ICCID)')
    pin = fields.Char(string='PIN', size=4, help='SIM card PIN code')
    puk = fields.Char(string='PUK', size=8, help='SIM card PUK unlock code')
    sms_cap_plan = fields.Char(string='SMS Cap Plan', help='Contracted SMS cap plan')
    calls_cap_plan = fields.Char(string='Calls Cap Plan', help='Contracted calls cap plan')
    gprs_cap_plan = fields.Char(string='GPRS Cap Plan', help='Contracted GPRS data cap plan')
    sms_package = fields.Char(string='SMS Package', help='Included SMS package (e.g. "100 SMS")')
    plan_rate = fields.Char(string='Plan/Rate', help='Main tariff plan name')
    gprs_package = fields.Char(string='GPRS Package', help='Contracted GPRS data package (e.g. "1GB")')
    serv = fields.Html(string='SERV.', help='Services')

    # Domain helper
    show_calls_code_as_password = fields.Boolean(compute="_compute_show_calls_code_as_password")

    # ============================================================
    # CONSTRAINTS
    # ============================================================
    _sql_constraints = [
        ('unique_number', 'unique(number)', 'This phone number is already registered!'),
        ('unique_imsi', 'unique(imsi)', 'IMSI must be unique!'),
        ('unique_sim_card', 'unique(sim_card)', 'SIM card serial number must be unique!'),
    ]

    @api.constrains('job_id', 'employee_ids')
    def _check_assignment(self):
        for rec in self:
            if rec.job_id and rec.employee_ids:
                invalid = rec.employee_ids.filtered(lambda e: e.job_id != rec.job_id)
                if invalid:
                    raise ValidationError(_("Employees %s do not belong to this job") % invalid.mapped('name'))

    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    @api.depends('employee_ids', 'job_id')
    def _compute_show_calls_code_as_password(self):
        current_user = self.env.user
        for mobile in self:
            # 1. Los managers siempre ven el código (sin puntos)
            if current_user.has_group('ict.group_ict_manager'):
                mobile.show_calls_code_as_password = False
                continue

            # 2. Usar el dominio base
            domain = [('job_id', '=', mobile.job_id.id)]

            # 3. Obtener los empleados asignados
            if mobile.employee_ids:
                domain.append(('id', 'in', mobile.employee_ids.employee_id.ids))
            authorized_employees = self.env['hr.employee'].search(domain)

            # 4. Verificar si el usuario actual está vinculado a algún empleado asignado
            if current_user.id in authorized_employees.user_id.ids:
                mobile.show_calls_code_as_password = False
            else:
                mobile.show_calls_code_as_password = True

    @api.depends('state')
    def _compute_state_date(self):
        for line in self:
            line.state_date = fields.Date.today()

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.employee_ids:
            self.employee_ids = [(5, 0, 0)]  # Limpia empleados

    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        if self.employee_ids:
            if self.state != 'assigned':
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

    # ============================================================
    # OVERRIDE METHODS
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            # Agregar código de país al número de teléfono
            if not line.number.startswith('+'):
                line.number = '+53 ' + line.number  # default Cuba
        return lines

    def write(self, vals):
        res = super().write(vals)
        # Agregar código de país al número de teléfono
        if 'number' in vals:
            for line in self:
                if not line.number.startswith('+'):
                    line.number = '+53 ' + vals['number']  # default Cuba
        return res

    # def _sync_employee_mobile(self):
    #     """Sincroniza el número de móvil del empleado con esta línea si es la línea principal."""
    #     if self.employee_id and self.number:
    #         # Actualizar el campo mobile_phone en hr.employee
    #         hr_emp = self.employee_id.employee_id
    #         if hr_emp:
    #             # Solo actualizar si no hay otro número más reciente
    #             # Puedes decidir si siempre sobrescribir o si solo si está vacío
    #             if not hr_emp.mobile_phone:
    #                 hr_emp.mobile_phone = self.number
    #             else:
    #                 # Si ya tiene número, podrías actualizar solo si es la línea principal
    #                 # Aquí decides la política: por ejemplo, siempre usar la primera línea asignada
    #                 pass