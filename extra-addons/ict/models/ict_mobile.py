# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ICTMobile(models.Model):
    _name = 'ict.mobile'
    _description = 'ICT Mobile'
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
        help='Equipment-related data of the mobile'
    )

    brand = fields.Char(string='Brand', required=True)
    storage_gb = fields.Integer(string='Storage (GB)', help='Internal storage capacity')
    ram_gb = fields.Integer(string='RAM (GB)', help='RAM memory')
    processor_model = fields.Char(string='Processor', help='Processor Model')
    mac_address = fields.Char(string='MAC Address', help='Wi-Fi/Bluetooth MAC')
    battery_capacity = fields.Integer(string='Battery (mAh)')
    screen_resolution = fields.Char(string='Screen Resolution', help='e.g., 1080x2400')
    screen_size = fields.Float(string='Screen Size (inches)')
    purchase_date = fields.Date(string='Purchase Date', default=fields.Date.today())
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
    line_ids = fields.One2many(
        string='Mobile Line',
        comodel_name='ict.mobile.line',
        inverse_name='mobile_id',
    )
    employee_ids = fields.Many2many(
        'ict.employee', 
        'ict_mobile_employee_rel', 
        'mobile_id', 
        'employee_id', 
        'Employees', 
        tracking=True, 
        ondelete='restrict', 
        compute='_compute_employee_ids', 
        help="Employee currently assigned to this mobile device", 
    )
    responsible_name = fields.Char(
        string='Responsible', 
        compute='_compute_responsible', 
        store=True, 
        help="The first employee selected will be considered the team's top manager.", 
    )
    
    # SIM / IMEI (IMEI se guarda en serial_no heredado)
    imei2 = fields.Char(string='IMEI2', size=15, help='Second IMEI for dual SIM devices')
    sim_type = fields.Selection([
        ('physical', 'Physical SIM'),
        ('esim', 'eSIM'),
        ('dual', 'Dual SIM'),
    ], string='SIM Type', default='dual')
    
    # Asignaciones
    # assignment_history_ids = fields.One2many(
    #     'ict.mobile.assignment',
    #     'mobile_id',
    #     string='Assignment History'
    # )

    # ============================================================
    # CONSTRAINS
    # ============================================================
    _sql_constraints = [
        ('unique_imei2', 'unique(imei2)', 'Another asset already exists with this serial number!'),
        ('unique_mac', 'unique(mac_address)', 'There is already another asset with this MAC address!'),
    ]

    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    @api.depends('brand', 'model', 'line_ids', 'line_ids.number')
    def _compute_display_name(self):
        for mobile in self:
            parts = []

            # Añadir marca y modelo
            if mobile.brand:
                parts.append(mobile.brand)
            if mobile.model:
                parts.append(mobile.model)

            # Procesar número de extensiones
            numbers = mobile.line_ids.mapped('number')
            if numbers:
                parts.append("- " + " ".join(numbers))

            # Asignar el nombre
            mobile.display_name = " ".join(parts) or "Unnamed Mobile"
            mobile.name = mobile.display_name

    @api.depends('line_ids', 'line_ids.employee_ids')
    def _compute_employee_ids(self):
        for emp in self:
            employees = emp.line_ids.mapped('employee_ids')
            emp.employee_ids = [(6, 0, employees.ids)]

    @api.depends('employee_ids')
    def _compute_responsible(self):
        for mobile in self:
            if mobile.employee_ids:
                # Asumimos primer empleado como responsable
                responsible = mobile.employee_ids[0].employee_id
                if responsible != mobile.equipment_id.employee_id:
                    mobile.equipment_id.employee_id = responsible
                if responsible.name != mobile.responsible_name:
                    mobile.responsible_name = responsible.name
            else:
                mobile.responsible_name = False
                mobile.equipment_id.employee_id = False

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        if self.line_ids:
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

    # def write(self, vals):
    #     # Detectar cambio de empleado
    #     if 'ict_employee_id' in vals:
    #         new_employee_id = vals['ict_employee_id']
    #         for mobile in self:
    #             old_employee = mobile.ict_employee_id
    #             if old_employee and new_employee_id and old_employee.id != new_employee_id:
    #                 # Se está reasignando a otro empleado sin desasignar primero
    #                 # Lanzar advertencia con opción a forzar (usaremos un contexto)
    #                 if not self.env.context.get('force_reassign'):
    #                     raise UserError(
    #                         _("This mobile is already assigned to %s. Please unassign it first or use the force reassign option."),
    #                         old_employee.name
    #                     )
    #                 else:
    #                     # Forzar reasignación: desasignar empleado para luego asignar normalmente
    #                     mobile.ict_employee_id = False
    #     return super().write(vals)

# ============================================================
# AUXILIARY MODELS
# ============================================================
# class ICTMobileAssignment(models.Model):
#     _name = 'ict.mobile.assignment'
#     _description = 'Mobile Assignment History'
#     _order = 'assign_date desc'

#     mobile_id = fields.Many2one('ict.mobile', string='Mobile', required=True, ondelete='cascade')
#     employee_id = fields.Many2one('ict.employee', string='Employee', required=True)
#     assign_date = fields.Date(string='Assignment Date', required=True, default=fields.Date.today)
#     return_date = fields.Date(string='Return Date')
#     notes = fields.Char(string='Notes')

