# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

_logger = logging.getLogger(__name__)

class ICTEmployee(models.Model):
    _name = 'ict.employee'
    _description = 'ICT Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Domain
    domain_user = fields.Char(string='Username *', required=True, tracking=True)
    domain_id = fields.Many2one(string='Domain *', comodel_name='mail.alias.domain', required=True, default=lambda self: self.env.company.alias_domain_id.id)
    work_email = fields.Char(string='Work Email', compute='_compute_work_email', store=True)
    hire_date = fields.Date(string='Hire Date', default=fields.Date().today())

    # Computes
    computer_ids = fields.Many2many('ict.computer', 'ict_computer_employee_rel', 'employee_id', 'computer_id', 'Computers')

    # Phones
    extension_ids = fields.Many2many('ict.phone.extension', 'ict_extension_employee_rel', 'employee_id', 'extension_id', 'Phone Extensions')
    work_phone = fields.Char(string='Work Phone', compute='_compute_work_phone', store=True)
    phone_ids = fields.Many2many('ict.phone', 'ict_phone_employee_rel', 'employee_id', 'phone_id', 'Phones', compute='_compute_phone_ids')
    
    # Mobiles
    line_ids = fields.Many2many('ict.mobile.line', 'ict_line_employee_rel', 'employee_id', 'line_id', 'Mobiles Line')
    mobile_phone = fields.Char(string='Mobile Phone', compute='_compute_mobile_phone', store=True)
    mobile_ids = fields.Many2many('ict.mobile', 'ict_mobile_employee_rel', 'employee_id', 'mobile_id', 'Mobiles', compute='_compute_mobile_ids')

    # Related employee fields
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee *', required=True, tracking=True)
    name = fields.Char(string="Name *", related='employee_id.name')
    user_id = fields.Many2one(related='employee_id.user_id')
    user_partner_id = fields.Many2one(related='employee_id.user_id.partner_id', related_sudo=False)
    user_status = fields.Selection(related='employee_id.user_id.state')
    job_id = fields.Many2one(related='employee_id.job_id')
    job_title = fields.Char(related='employee_id.job_title')
    department_id = fields.Many2one(related='employee_id.department_id')
    department_name = fields.Char(related='employee_id.department_id.name')
    image_1920 = fields.Binary(related='employee_id.image_1920', attachment=True)
    
    # Fields for views
    whatsapp_url = fields.Char(string='WhatsApp Link', compute='_compute_social_urls')
    telegram_url = fields.Char(string='Telegram Link', compute='_compute_social_urls')
    formatted_hire_date = fields.Char(string='Hire Date Formatted', compute='_compute_formatted_hire_date')
    department_hex_color = fields.Char(string='Department Hex Color', compute='_compute_department_hex_color', store=False)

    # ============================================================
    # CONSTRAINS
    # ============================================================
    _sql_constraints = [
        ('unique_user', 'unique(domain_user)', 'The username already exists.'),
    ]

    @api.constrains('work_email')
    def _check_email(self):
        for record in self:
            if record.work_email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.work_email):
                raise ValidationError("Invalid email format")

    @api.constrains('extension_ids', 'line_ids', 'job_id', 'department_id')
    def _check_assignment(self):
        for employee in self:
            if not employee.job_id and not employee.department_id:
                continue

            # Extensions
            if employee.extension_ids:
                invalid_extensions = employee.extension_ids.filtered(
                    lambda ext: (
                        (ext.assign_to == 'job' and ext.job_id != employee.job_id) or
                        (ext.assign_to == 'department' and ext.department_id != employee.department_id)
                    )
                )
                if invalid_extensions:
                    raise ValidationError(
                        _("The following extensions are not compatible with this employee's job or department: %s")
                        % ', '.join(invalid_extensions.mapped('number'))
                    )
            
            # Lines
            if employee.line_ids:
                invalid_lines = employee.line_ids.filtered(
                    lambda line: (
                        (line.job_id != employee.job_id)
                    )
                )
                if invalid_lines:
                    raise ValidationError(
                        _("The following mobile line are not compatible with this employee's job: %s")
                        % ', '.join(invalid_lines.mapped('number'))
                    )
            
    
    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    @api.depends('line_ids', 'line_ids.mobile_id')
    def _compute_mobile_ids(self):
        for emp in self:
            mobiles = emp.line_ids.mapped('mobile_id')
            emp.mobile_ids = [(6, 0, mobiles.ids)]

    @api.depends('extension_ids', 'extension_ids.phone_id')
    def _compute_phone_ids(self):
        for emp in self:
            phones = emp.extension_ids.mapped('phone_id')
            emp.phone_ids = [(6, 0, phones.ids)]

    @api.depends('extension_ids', 'extension_ids.number')
    def _compute_work_phone(self):
        for emp in self:
            numbers = emp.extension_ids.mapped('number')
            emp.work_phone = " ".join(numbers) if numbers else ""
            if emp.employee_id and emp.employee_id.work_phone != emp.work_phone:
                emp.employee_id.work_phone = emp.work_phone


    @api.depends('line_ids', 'line_ids.number')
    def _compute_mobile_phone(self):
        for emp in self:
            numbers = emp.line_ids.mapped('number')
            emp.mobile_phone = " ".join(numbers) if numbers else ""
            if emp.employee_id and emp.employee_id.mobile_phone != emp.mobile_phone:
                emp.employee_id.mobile_phone = emp.mobile_phone

    @api.depends('domain_id', 'domain_user')
    def _compute_work_email(self):
        for emp in self:
            if emp.domain_id and emp.domain_user:
                emp.work_email = emp.domain_user + '@' + emp.domain_id.name
            else:
                emp.work_email = False
            if emp.employee_id and emp.employee_id.work_email != emp.work_email:
                emp.employee_id.work_email = emp.work_email

    @api.depends('line_ids', 'line_ids.number')
    def _compute_social_urls(self):
        for rec in self:
            if not rec.line_ids:
                rec.whatsapp_url = 'https://web.whatsapp.com/'
                rec.telegram_url = 'https://web.telegram.org/'
                continue
            
            # Se tomará el primer número por simplicidad
            phone_number = rec.line_ids[0].number
            
            # Eliminar todo excepto dígitos y un posible '+' inicial
            clean = re.sub(r'[^\d+]', '', phone_number)
            
            # Si no empieza por +, asumimos código de país
            if not clean.startswith('+'):
                clean = '+53' + clean  # default Cuba
            
            rec.whatsapp_url = f'https://wa.me/{clean}'
            rec.telegram_url = f'https://t.me/{clean}'

    @api.depends('hire_date')
    def _compute_formatted_hire_date(self):
        for rec in self:
            rec.formatted_hire_date = rec.hire_date.strftime('%b %Y') if rec.hire_date else False

    @api.depends('department_id', 'department_id.color')
    def _compute_department_hex_color(self):
        """ Diccionario que mapea el índice de color estándar de Odoo a su valor hexadecimal """
        DEPT_COLOR_PALETTE = {
            0: '#3b5998',  # azul oscuro (sin color suele ser este)
            1: '#F06050',  # rojo
            2: '#F4A460',  # naranja
            3: '#F7CD1F',  # amarillo
            4: '#6CC1ED',  # celeste
            5: '#814968',  # morado
            6: '#8C8C8C',  # gris
            7: '#2E86D1',  # azul
            8: '#20B2AA',  # verde agua
            9: '#4CAF50',  # verde
            10: '#D2691E', # marrón
            11: '#E67E22', # naranja oscuro
        }
        for rec in self:
            color_int = rec.department_id.color
            rec.department_hex_color = DEPT_COLOR_PALETTE.get(color_int, '#adb5bd')

    # ============================================================
    # ACTION METHODS
    # ============================================================
    def action_send_email(self):
        """ Método para abrir el compositor de correo """
        self.ensure_one()
        ctx = {
            'default_model': 'ict.employee',
            'default_res_ids': [self.id],
            'default_email_to': self.work_email,
            'default_partner_ids': [self.employee_id.work_contact_id.id] 
                                    if self.employee_id.work_contact_id and self.employee_id.work_contact_id.id != self.env.user.partner_id.id 
                                    else False,
            'default_subject': 'Mensaje de ICT'
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    def action_post_note(self):
        """ Método para abrir compositor de nota interna """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': {
                'default_model': 'ict.employee',
                'default_res_ids': [self.id],
                'default_composition_mode': 'comment',  # nota interna
                'default_subtype_id': self.env.ref('mail.mt_note').id,
                'force_email': False,
            },
        }
        
    def action_open_whatsapp(self):
        self.ensure_one()
        if self.whatsapp_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.whatsapp_url,
                'target': 'new',
            }
        return False

    def action_open_telegram(self):
        self.ensure_one()
        if self.telegram_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.telegram_url,
                'target': 'new',
            }
        return False

    def action_open_facebook(self):
        self.ensure_one()
        if self.employee_id:
            return {
                'type': 'ir.actions.act_url',
                'url': 'https://www.facebook.com/empresadecigarros.lazaropena.7',
                'target': 'new',
            }
        return False

    def action_open_x(self):
        self.ensure_one()
        if self.employee_id:
            return {
                'type': 'ir.actions.act_url',
                'url': 'https://x.com/CigarrosHolguin',
                'target': 'new',
            }
        return False