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
        tracking=True,
        help="Employee currently assigned to this phone device"
    )
    ict_employee_name = fields.Char(related='ict_employee_id.name')
    
    # SIM / IMEI (IMEI se guarda en serial_no heredado)
    imei2 = fields.Char(string='IMEI2', size=15, help='Second IMEI for dual SIM devices')
    sim_type = fields.Selection([
        ('physical', 'Physical SIM'),
        ('esim', 'eSIM'),
        ('dual', 'Dual SIM'),
    ], string='SIM Type', default='dual')
    
    # Asignaciones
    assign_date = fields.Date('Assigned Date', tracking=True, compute="_compute_assign_date")
    assignment_history_ids = fields.One2many(
        'ict.phone.assignment',
        'phone_id',
        string='Assignment History'
    )

    # ============================================================
    # CONSTRAINS
    # ============================================================
    _sql_constraints = [
        ('unique_equipment', 'unique(equipment_id)', 'This equipment is already linked to a phone.'),
        ('unique_imei2', 'unique(imei2)', "Another asset already exists with this serial number!"),
        ('unique_mac', 'unique(mac_address)', "There is already another asset with this MAC address!"),
    ]

    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    @api.depends("ict_employee_id")
    def _compute_assign_date(self):
        for phone in self:
            if phone.ict_employee_id:
                phone.assign_date = fields.Date.today()
            else:
                phone.assign_date = False

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange('brand', 'model')
    def _onchange_name(self):
        if self.brand and self.model and not self.name:
            self.name = f"{self.brand} {self.model}"

    @api.onchange('ict_employee_id')
    def _onchange_ict_employee(self):
        if self.ict_employee_id:
            employee = self.ict_employee_id
            # Cambiar a estado asignado de ser diferente
            if self.state != 'assigned':
                self.state = 'assigned'
            # Sincronizar campo de empleado en equipment
            self.equipment_id.employee_id = employee.employee_id
            # Actualizar nombre si coincide con el autogenerado (marca+modelo)
            if self.name == f"{self.brand} {self.model}":
                if employee.name:
                    self.name = f"{self.brand} {self.model} - {employee.name.split()[0]}"
        else:
            # Si se quita el empleado, desvincular y cambiar estado
            self.state = 'available'
            self.equipment_id.employee_id = False

    # ============================================================
    # ACTION METHODS
    # ============================================================
    def action_send_repair(self):
        self.state = 'repair'

    def action_retire(self):
        self.state = 'retired'
        # Desvincular empleado al retirar
        self.ict_employee_id = False

    # ============================================================
    # STATS
    # ============================================================
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

    # ============================================================
    # OVERRIDE METHODS
    # ============================================================
    def write(self, vals):
        # Detectar cambio de empleado
        if 'ict_employee_id' in vals:
            new_employee_id = vals['ict_employee_id']
            for phone in self:
                old_employee = phone.ict_employee_id
                if old_employee and new_employee_id and old_employee.id != new_employee_id:
                    # Se está reasignando a otro empleado sin desasignar primero
                    # Lanzar advertencia con opción a forzar (usaremos un contexto)
                    if not self.env.context.get('force_reassign'):
                        raise UserError(
                            _("This phone is already assigned to %s. Please unassign it first or use the force reassign option."),
                            old_employee.name
                        )
                    else:
                        # Forzar reasignación: desasignar empleado para luego asignar normalmente
                        phone.ict_employee_id = False
        return super().write(vals)

# ============================================================
# AUXILIARY MODELS
# ============================================================
class ICTPhoneAssignment(models.Model):
    _name = 'ict.phone.assignment'
    _description = 'Phone Assignment History'
    _order = 'assign_date desc'

    phone_id = fields.Many2one('ict.phone', string='Phone', required=True, ondelete='cascade')
    employee_id = fields.Many2one('ict.employee', string='Employee', required=True)
    assign_date = fields.Date(string='Assignment Date', required=True, default=fields.Date.today)
    return_date = fields.Date(string='Return Date')
    notes = fields.Char(string='Notes')

