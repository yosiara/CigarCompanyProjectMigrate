# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ICTPhone(models.Model):
    _name = 'ict.phone'
    _description = 'ICT Phone'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'maintenance.equipment': 'equipment_id'}

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Related Equipment',
        required=True,
        ondelete='restrict',
        auto_join=True,
        index=True,
        help='Equipment-related data of the phone'
    )

    # Inherited Equipment Fields
    # # name = fields.Char('Equipment Name', required=True, translate=True)
    # # active = fields.Boolean(default=True)
    # # owner_user_id = fields.Many2one('res.users', string='Owner', tracking=True)
    # # category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category',
    # #                               tracking=True, group_expand='_read_group_category_ids')
    # # partner_id = fields.Many2one('res.partner', string='Vendor', check_company=True)
    # # partner_ref = fields.Char('Vendor Reference')
    # # location = fields.Char('Location')
    # # model = fields.Char('Model')
    # # serial_no = fields.Char('Serial Number', copy=False)
    # # assign_date = fields.Date('Assigned Date', tracking=True)
    # # cost = fields.Float('Cost')
    # # note = fields.Html('Note')
    # # warranty_date = fields.Date('Warranty Expiration Date')
    # # color = fields.Integer('Color Index')
    # # scrap_date = fields.Date('Scrap Date')
    # # maintenance_ids = fields.One2many('maintenance.request', 'equipment_id')
    # # equipment_properties = fields.Properties('Properties', definition='category_id.equipment_properties_definition', copy=True)
    # # match_serial = fields.Boolean(compute='_compute_match_serial')

    # Campos específicos de teléfono
    brand = fields.Char(string='Brand', required=True)
    phone_number = fields.Char(string='Phone Number', required=True)
    carrier = fields.Char(string='Carrier', default='ETECSA')
    storage_gb = fields.Integer(string='Storage (GB)', help='Internal storage capacity')
    ram_gb = fields.Integer(string='RAM (GB)', help='RAM memory')
    processor_model = fields.Char(string='Processor', help='Processor Model')
    mac_address = fields.Char(string='MAC Address', help='Wi-Fi/Bluetooth MAC')
    battery_capacity = fields.Integer(string='Battery (mAh)')
    screen_resolution = fields.Char(string='Screen Resolution', help='e.g., 1080x2400')
    screen_size = fields.Float(string='Screen Size (inches)')
    network_type = fields.Selection([
        ('5g', '5G'),
        ('4g', '4G/LTE'),
        ('3g', '3G'),
        ('2g', '2G'),
    ], string='Network Type', default='4g')
    camera_mp = fields.Char(string='Camera MP', help='Main camera megapixels')
    inventory_number = fields.Char(string='Inventory Number', copy=False)
    os = fields.Selection([
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('other', 'Other'),
    ], string='Operating System', default='android')
    os_version = fields.Char(string='OS Version')
    physical_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], string='Physical Condition', default='good')

    state = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('repair', 'Under Repair'),
        ('retired', 'Retired'),
    ], string='Status', default='available', tracking=True)
    
    ict_employee_id = fields.Many2one(
        string='Assigned ICT Employee',
        comodel_name='ict.employee',
        ondelete='restrict',
    )
    ict_employee_name = fields.Char(string="ICT Employee Name", related='ict_employee_id.name')
    
    # SIM / IMEI (IMEI se guarda en serial_no)
    iccid = fields.Char(string='ICCID', help='SIM card identifier')
    sim_type = fields.Selection([
        ('physical', 'Physical SIM'),
        ('esim', 'eSIM'),
        ('dual', 'Dual SIM'),
    ], string='SIM Type', default='physical')
    imei2 = fields.Char(string='IMEI2', help='Second IMEI for dual SIM devices')
    locked = fields.Boolean(string='Locked', help='Locked by carrier or MDM')
    mdm_managed = fields.Boolean(string='MDM Managed')
    
    # Asignaciones
    assign_date = fields.Date('Assigned Date', tracking=True, compute="_compute_assign_date")
    assignment_history_ids = fields.One2many(
        'ict.phone.assignment',
        'phone_id',
        string='Assignment History'
    )
    
    # SQL Constraints
    _sql_constraints = [
        ('unique_equipment', 'unique(equipment_id)', 'This equipment is already linked to a phone.'),
    ]

    @api.depends("ict_employee_id")
    def _compute_assign_date(self):
        for phone in self:
            if phone.ict_employee_id:
                phone.assign_date = fields.Date.today()
            else:
                phone.assign_date = False

    # Métodos de cambio de estado
    @api.onchange('ict_employee_id')
    def _onchange_employee_id(self):
        if self.ict_employee_id:
            self.state = 'assigned'
        else:
            self.state = 'available'

    # def action_assign(self):
    #     self.state = 'assigned'

    def action_send_repair(self):
        self.state = 'repair'

    def action_retire(self):
        self.state = 'retired'
        self.active = False

    # Método de estadísticas para kanban (similar a computer)
    @api.model
    def get_kanban_stats(self, options=None):
        """Get statistics for kanban view"""
        # Si se pasa last_month como opción, calcular estadísticas del mes anterior
        if options and options.get('last_month'):
            from datetime import datetime, timedelta
            today = datetime.now()
            first_day_current = today.replace(day=1)
            last_month = first_day_current - timedelta(days=1)
            first_day_last = last_month.replace(day=1)
            
            domain = [
                ('create_date', '>=', first_day_last.strftime('%Y-%m-%d')),
                ('create_date', '<=', last_month.strftime('%Y-%m-%d')),
                ('active', '=', True)
            ]
        else:
            domain = [('active', '=', True)]
        
        total = self.search_count(domain)
        
        # Get counts by state
        states = ['new', 'in_use', 'repair', 'retired']
        by_status = {}
        
        for state in states:
            state_domain = domain + [('state', '=', state)]
            count = self.search_count(state_domain)
            if count > 0 or options:  # Incluir cero si hay opciones para mantener estructura
                by_status[state] = count
        
        return {
            'total': total,
            'by_status': by_status
        }

    # Métodos de cambio de estado
    def action_assign(self):
        self.state = 'assigned'
        if not self.assignment_date:
            self.assignment_date = fields.Date.today()

    def action_send_repair(self):
        self.state = 'repair'

    def action_retire(self):
        self.state = 'retired'
        self.active = False

    @api.onchange('brand', 'model')
    def _onchange_name(self):
        if self.brand and self.model and not self.name:
            self.name = f"{self.brand} {self.model}"

    @api.onchange('ict_employee_id')
    def _onchange_employee_name(self):
        # Solo actualiza si el name coincide con el autogenerado (marca+modelo)
        if self.ict_employee_id and self.name == f"{self.brand} {self.model}":
            employee = self.ict_employee_id
            if employee.name:
                self.name = f"{self.brand} {self.model} - {employee.name.split()[0]}"

    @api.onchange('ict_employee_id')
    def _onchange_ict_employee(self):
        if self.ict_employee_id:
            self.equipment_id.employee_id = self.ict_employee_id.employee_id

# Modelo auxiliar para historial de asignaciones
class ICTPhoneAssignment(models.Model):
    _name = 'ict.phone.assignment'
    _description = 'Phone Assignment History'
    _order = 'assign_date desc'

    phone_id = fields.Many2one('ict.phone', string='Phone', required=True, ondelete='cascade')
    employee_id = fields.Many2one('ict.employee', string='Employee', required=True)
    assign_date = fields.Date(string='Assignment Date', required=True, default=fields.Date.today)
    return_date = fields.Date(string='Return Date')
    notes = fields.Char(string='Notes')

