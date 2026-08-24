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
    
    brand = fields.Char(string='Brand', required=True)
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
        ('unique_mac', 'unique(mac_address)', 'There is already another asset with this MAC address!'),
    ]

    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    @api.depends('brand', 'model', 'extension_ids', 'extension_ids.number')
    def _compute_display_name(self):
        for phone in self:
            parts = []

            # Añadir marca y modelo
            if phone.brand:
                parts.append(phone.brand)
            if phone.model:
                parts.append(phone.model)

            # Procesar número de extensiones
            ext_numbers = [ext.number for ext in phone.extension_ids if ext.number]
            if ext_numbers:
                parts.append("- " + " ".join(ext_numbers))

            # Asignar el nombre
            phone.display_name = " ".join(parts) or "Unnamed Phone"
            if phone.equipment_id and phone.equipment_id.name != phone.display_name:
                phone.equipment_id.name = phone.display_name

    @api.depends('extension_ids', 'extension_ids.employee_ids')
    def _compute_employee_ids(self):
        for emp in self:
            employees = emp.extension_ids.mapped('employee_ids')
            emp.employee_ids = [(6, 0, employees.ids)]

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================


    # @api.model_create_multi
    # def create(self, vals_list):
    #     extensions = super().create(vals_list)
    #     for ext in extensions:
    #         ext._sync_employee_work_phone()
    #         # Si es asignada a un empleado, marcar como principal si no hay otra
    #         if ext.employee_id and not ext.is_primary:
    #             ext._ensure_primary_extension()
    #     return extensions

    # def write(self, vals):
    #     # Guardar cambios de employee_id o number para sincronizar después
    #     old_employees = {ext.id: ext.employee_id for ext in self}
    #     res = super().write(vals)
        
    #     # Sincronizar el teléfono de trabajo del empleado
    #     if 'employee_id' in vals or 'number' in vals or 'is_primary' in vals:
    #         for ext in self:
    #             ext._sync_employee_work_phone()
        
    #     # Si se desasignó de un empleado, recalcular su work_phone desde otras extensiones
    #     if 'employee_id' in vals and not vals.get('employee_id'):
    #         for ext in self:
    #             old_emp = old_employees.get(ext.id)
    #             if old_emp:
    #                 old_emp._update_work_phone_from_extensions()
        
    #     # Si se asignó a un empleado y no es principal, asegurar una principal
    #     if 'employee_id' in vals and vals.get('employee_id'):
    #         for ext in self:
    #             if not ext.is_primary:
    #                 ext._ensure_primary_extension()
        
    #     return res

    # def _sync_employee_work_phone(self):
    #     """Sincroniza el work_phone del empleado con esta extensión si es la principal."""
    #     if self.employee_id and self.is_primary and self.number:
    #         hr_emp = self.employee_id.employee_id
    #         if hr_emp and hr_emp.work_phone != self.number:
    #             hr_emp.work_phone = self.number

    # def _ensure_primary_extension(self):
    #     """Asegura que haya una extensión principal para el empleado."""
    #     if not self.employee_id:
    #         return
        
    #     # Buscar si ya hay una principal
    #     primary = self.search([
    #         ('employee_id', '=', self.employee_id.id),
    #         ('is_primary', '=', True),
    #     ], limit=1)
        
    #     if not primary:
    #         # No hay principal, marcar esta como principal
    #         self.is_primary = True
    #         # Sincronizar work_phone
    #         self._sync_employee_work_phone()
    #     elif primary != self and self.is_primary:
    #         # Si esta es principal pero ya hay otra, desmarcar esta
    #         self.is_primary = False
    #         # Asegurar que la otra sigue siendo principal (ya lo es)

    # def action_set_primary(self):
    #     """Acción para marcar esta extensión como principal desde el formulario."""
    #     self.ensure_one()
    #     if self.employee_id:
    #         # Desmarcar otras principales del mismo empleado
    #         self.search([
    #             ('employee_id', '=', self.employee_id.id),
    #             ('is_primary', '=', True),
    #         ]).write({'is_primary': False})
    #         self.is_primary = True
    #         self._sync_employee_work_phone()
    #     else:
    #         raise UserError(_("Cannot set as primary: no employee assigned."))