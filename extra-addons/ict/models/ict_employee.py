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
    image_1920 = fields.Binary(related='employee_id.image_1920', string="Photo", attachment=True)
    
    @api.depends('domain_id', 'domain_user')
    def _compute_work_email(self):
        for employee in self:
            if employee.domain_id and employee.domain_user:
                employee.work_email = employee.domain_user + '@' + employee.domain_id.name
            else:
                employee.work_email = False
            employee.employee_id.work_email = employee.work_email

    @api.constrains('work_email')
    def _check_email(self):
        for record in self:
            if record.work_email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.work_email):
                raise ValidationError("Invalid email format")

    # Campo para enlace de WhatsApp limpio (solo números, con prefijo internacional si se desea)
    whatsapp_url = fields.Char(string='WhatsApp Link', compute='_compute_whatsapp_url')

    @api.depends('mobile_phone')
    def _compute_whatsapp_url(self):
        for rec in self:
            url = False
            if rec.mobile_phone:
                # Eliminar todo excepto dígitos y un posible + inicial
                clean = re.sub(r'[^\d+]', '', rec.mobile_phone)
                # Si no empieza por +, asumimos código de país (ajústalo según tu zona)
                if not clean.startswith('+'):
                    clean = '+34' + clean  # ejemplo España
                url = f'https://wa.me/{clean}'
            rec.whatsapp_url = url

    # Método para abrir el compositor de correo con el destinatario precargado
    def action_send_email(self):
        self.ensure_one()
        ctx = {
            'default_model': 'ict.employee',
            'default_res_id': self.id,
            'default_email_to': self.work_email,
            'default_partner_ids': self.employee_id.work_contact_id.id if self.employee_id.work_contact_id else False,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    # Reemplazar el uso de t-options por este campo computado
    formatted_hire_date = fields.Char(string='Hire Date Formatted', compute='_compute_formatted_hire_date')

    @api.depends('hire_date')
    def _compute_formatted_hire_date(self):
        for rec in self:
            rec.formatted_hire_date = rec.hire_date.strftime('%b %Y') if rec.hire_date else False

    # Método para abrir compositor de nota interna (sustituye al botón de chatter redundante)
    def action_post_note(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': {
                'default_model': 'ict.employee',
                'default_res_id': self.id,
                'default_composition_mode': 'comment',  # nota interna
                'default_subtype_id': self.env.ref('mail.mt_note').id,
                'force_email': False,
            },
        }