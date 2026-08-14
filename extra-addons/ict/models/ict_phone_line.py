# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class IctPhoneLine(models.Model):
    _name = 'ict.phone.line'
    _description = 'ICT Phone Line'
    _rec_name = 'phone_number'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='ict.employee',
        ondelete='restrict',
        tracking=True,
        help="Employee to whom this line is assigned"
    )
    phone_number = fields.Char(
        string='Phone Number',
        required=True,
        index=True,
        help='Phone number of the line'
    )
    state = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='available', tracking=True)

    assign_date = fields.Date('Assignment Date', tracking=True, compute="_compute_assign_date")
    activation_date = fields.Date(string='Activation Date')
    cancellation_date = fields.Date(string='Cancellation Date')
    carrier = fields.Char(string='Carrier', default='ETECSA')

    # ETECSA data
    imsi = fields.Char(string='IMSI', help='International Mobile Subscriber Identity')
    sim_card = fields.Char(string='SIM Card', help='SIM card serial number (ICCID)')
    pin = fields.Char(string='PIN', size=4, help='SIM card PIN code')
    puk = fields.Char(string='PUK', size=8, help='SIM card PUK unlock code')
    secondary_language = fields.Char(string='Secondary Language', help='Secondary language configured on the line')
    written_language = fields.Char(string='Written Language', help='Preferred written language')
    sms_cap_plan = fields.Char(string='SMS Cap Plan', help='Contracted SMS cap plan')
    calls_cap_plan = fields.Char(string='Calls Cap Plan', help='Contracted calls cap plan')
    roaming_cap_plan = fields.Char(string='Roaming Cap Plan', help='Contracted roaming cap plan')
    gprs_cap_plan = fields.Char(string='GPRS Cap Plan', help='Contracted GPRS data cap plan')
    sms_package = fields.Char(string='SMS Package', help='Included SMS package (e.g. "100 SMS")')
    plan_rate = fields.Char(string='Plan/Rate', help='Main tariff plan name')
    gprs_package = fields.Char(string='GPRS Package', help='Contracted GPRS data package (e.g. "1GB")')
    gprs_profile = fields.Char(string='GPRS Profile', help='GPRS/APN connection profile')
    serv = fields.Char(string='SERV.', help='Services')

    # ============================================================
    # CONSTRAINTS
    # ============================================================
    _sql_constraints = [
        ('unique_phone_number', 'unique(phone_number)', 'This phone number is already registered.'),
    ]

    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    @api.depends("employee_id")
    def _compute_assign_date(self):
        for phone in self:
            if phone.employee_id:
                phone.assign_date = fields.Date.today()
            else:
                phone.assign_date = False

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            # Agregar código de país al número de teléfono
            if not line.phone_number.startswith('+'):
                line.phone_number = '+53 ' + line.phone_number  # default Cuba
        return lines

    def write(self, vals):
        res = super().write(vals)
        # Agregar código de país al número de teléfono
        if 'phone_number' in vals:
            for line in self:
                if not line.phone_number.startswith('+'):
                    line.phone_number = '+53 ' + vals['phone_number']  # default Cuba
        return res

    # def _sync_employee_mobile(self):
    #     """Sincroniza el número de móvil del empleado con esta línea si es la línea principal."""
    #     if self.employee_id and self.phone_number:
    #         # Actualizar el campo mobile_phone en hr.employee
    #         hr_emp = self.employee_id.employee_id
    #         if hr_emp:
    #             # Solo actualizar si no hay otro número más reciente
    #             # Puedes decidir si siempre sobrescribir o si solo si está vacío
    #             if not hr_emp.mobile_phone:
    #                 hr_emp.mobile_phone = self.phone_number
    #             else:
    #                 # Si ya tiene número, podrías actualizar solo si es la línea principal
    #                 # Aquí decides la política: por ejemplo, siempre usar la primera línea asignada
    #                 pass