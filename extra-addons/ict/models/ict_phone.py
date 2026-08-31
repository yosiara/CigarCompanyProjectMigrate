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

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Related Equipment',
        required=True,
        ondelete='restrict',
        auto_join=True,
        index=True,
        help='Equipment-related data of the phone'
    )
    
    brand = fields.Char(string='Brand *', required=True)
    mac_address = fields.Char(string='MAC Address')
    ip_address = fields.Char(string='IP Address')
    poe_support = fields.Boolean(string='PoE Support', default=False, help='Power over Ethernet')
    has_screen = fields.Boolean(string='Has Screen', default=True)
    network_ports = fields.Integer(string='Network Ports', default=2)
    purchase_date = fields.Date(string='Purchase Date', default=fields.Date.today())
    extension_ids = fields.One2many(
        string='Phone Extension',
        comodel_name='ict.phone.extension',
        inverse_name='phone_id',
    )
    employee_ids = fields.Many2many(
        'ict.employee', 
        'ict_phone_employee_rel', 
        'phone_id', 
        'employee_id', 
        'Employees', 
        tracking=True, 
        ondelete='restrict', 
        compute='_compute_employee_ids', 
        help="Employee currently assigned to this phone device", 
    )
    phone_type = fields.Selection([
        ('analog', 'Analógico'),
        ('digital', 'Digital'),
        ('voip', 'VoIP'),
        ('ip', 'IP'),
    ], string='Phone Type', default='voip')
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
    
    # ============================================================
    # CONSTRAINS
    # ============================================================
    _sql_constraints = [
        ('unique_equipment', 'unique(equipment_id)', 'There is already another asset with this maintenance equipment!'),
        ('unique_mac', 'unique(mac_address)', 'There is already another asset with this MAC address!'),
        ('unique_ip', 'unique(ip_address)', 'There is already another asset with this IP address!'),
    ]

    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    def _compute_equipment_name(self):
        self.ensure_one()
        parts = []
        if self.brand:
            parts.append(self.brand)
        if self.model:
            parts.append(self.model)
        ext_numbers = [ext.number for ext in self.extension_ids if ext.number]
        if ext_numbers:
            parts.append("- " + " ".join(ext_numbers))
        return " ".join(parts) or "Unnamed Phone"
    
    @api.depends('brand', 'model', 'extension_ids', 'extension_ids.number')
    def _compute_display_name(self):
        for phone in self:
            phone.display_name = phone._compute_equipment_name()
            phone.name = phone.display_name

    @api.depends('extension_ids', 'extension_ids.employee_ids')
    def _compute_employee_ids(self):
        for emp in self:
            employees = emp.extension_ids.mapped('employee_ids')
            emp.employee_ids = [(6, 0, employees.ids)]

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange('extension_ids')
    def _onchange_extension_ids(self):
        if self.extension_ids:
            if self.state != 'assigned':
                self.state = 'assigned'
            self.assign_date = fields.Date.today()
        else:
            self.state = 'available'
            self.assign_date = False

    # ============================================================
    # ACTION METHODS
    # ============================================================
    def action_send_repair(self):
        self.state = 'repair'

    def action_retire(self):
        self.state = 'retired'
        # Desvincular empleado al retirar
        self.employee_ids = False

    # ============================================================
    # OVERRIDE METHODS
    # ============================================================
    def unlink(self):
        """Clear equipment models records"""
        equipment_ids = self.mapped('equipment_id')
        result = super().unlink()
        if equipment_ids:
            try:
                equipment_ids.unlink()
            except UserError as e:
                _logger.error(e)
                raise UserError(_("Cannot delete the associated equipment because it has other dependencies. Please remove those dependencies first."))
        return result