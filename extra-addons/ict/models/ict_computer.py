# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ICTComputer(models.Model):
    _name = 'ict.computer'
    _description = 'Computer Inventory'
    _inherits = {'maintenance.equipment': 'equipment_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']

    equipment_id = fields.Many2one('maintenance.equipment', required=True, ondelete='cascade', auto_join=True, index=True,
        string='Related Equipment', help='Equipment-related data of the computer')

    type = fields.Selection([
        ('desktop', 'Desktop'),
        ('laptop', 'Laptop'),
        ('server', 'Server'),
    ], string='Type', required=True, default='desktop')

    brand = fields.Char(string='Brand', required=True)
    # model = fields.Char(string='Model', required=True)
    # processor = fields.Char(string='Processor')
    # ram_gb = fields.Integer(string='RAM (GB)')
    total_ram_gb = fields.Integer(string='Total RAM (GB)', compute='_compute_total_ram_gb')
    # storage_gb = fields.Integer(string='Storage (GB)')
    total_storage_gb = fields.Integer(string='Total Storage (GB)', compute='_compute_total_storage_gb')
    # storage_type = fields.Selection([
    #     ('hdd', 'HDD'),
    #     ('ssd', 'SSD'),
    #     ('nvme', 'NVMe'),
    # ], string='Storage Type')
    
    operating_system = fields.Selection([
        ('windows_10', 'Windows 10'),
        ('windows_11', 'Windows 11'),
        ('windows_server', 'Windows Server'),
        ('linux', 'Linux'),
        ('macos', 'macOS'),
    ], string='Operating System')
    
    ip_address = fields.Char(string='IP Address')
    # mac_address = fields.Char(string='MAC Address')
    
    # employee_id = fields.Many2one('ict.employee', string='Assigned to')

    purchase_date = fields.Date(string='Purchase Date')
    # warranty_date = fields.Date(string='Warranty End Date')
    supplier = fields.Char(string='Supplier')
    state = fields.Selection([
        ('new', 'New'),
        ('in_use', 'In Use'),
        ('repair', 'Under Repair'),
        ('retired', 'Retired'),
    ], string='Status', default='new')
    
    ##########################################
    employee_ids = fields.Many2many('ict.employee',
                        'ict_computer_employees_rel',
                        'computer_id', 'employee_id', 'Assigned Employees'
                    )
    responsible_id = fields.Float(string='Responsible', 
        compute='_compute_responsible', inverse='_set_responsible',
        help=_("The first of the selected employees will be assumed as responsible for the equipment/computer and their equal in maintenance")
    )
    responsible_name = fields.Char(related='responsible_id.name')
    # equipment_assign_to = fields.Selection(selection_add=[('employees', 'Employees')])
    inventory_number = fields.Char('Inventory Number')
    seal = fields.Char('Seal')
    ocs_external_id = fields.Integer(index=True)
    # is_a_computer = fields.Boolean('Is an ICT equipment?', default=False)

    # Administrative data...
    user_name = fields.Char()
    # operative_system = fields.Char()
    # os_version = fields.Char()

    # uuid = fields.Char()
    # architecture = fields.Char()

    # domain = fields.Char()
    # ip_address = fields.Char()
    information_updated_date = fields.Datetime()

    # To know the state in the importation...
    # 1 -> Imported.
    # 2 -> Updated first time.
    # 3 -> Updated more than once time.
    # importation_state = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')], default='1')

    # local_id = fields.Many2one('l10n_cu_locals.local', 'Used in local')

    component_ids = fields.One2many(
        'ict.computer.component', 'computer_id', 'Component', domain=[('is_active', '=', True)]
    )
    component_id = fields.Many2one(comodel_name='ict.computer.component', compute='_compute_component', search='_search_computer_component', store=False)
    component_type = fields.Char(related='component_id.type')

    # software_ids = fields.One2many('equipment.software', 'equipment_id', 'Software')

    # qrcode_image = fields.Binary("QRCode", compute='get_qrimage')

    _sql_constraints = [
        ('equipment_id', 'unique(equipment_id)', "Related equipment already exists!"),
    ]

    @api.onchange('equipment_assign_to')
    def _onchange_equipment_assign_to(self):
        if self.equipment_assign_to == 'department':
            self.employee_ids = False

    @api.depends('employee_ids')
    def _compute_responsible(self):
        for rec in self:
            if rec.employee_ids:
                rec.responsible_id = rec.employee_ids[0]

    @api.onchange('responsible_id')
    def _set_responsible(self):
        if self.responsible_id:
            self.equipment_id.employee_id = self.responsible_id

    @api.depends('component_ids')
    def _compute_component(self):
        component_per_computer = {
            component.computer_id.id: component
            for component in self.env['ict.computer.component'].search([('computer_id', 'in', self.ids)])
        }
        for computer in self:
            computer.component_id = component_per_computer.get(computer.id)

    def _search_computer_component(self, operator, value):
        return [('component_ids', operator, value)]

    # @api.model
    # def get_kanban_stats(self):
    #     """Get statistics for kanban view"""
    #     total = self.search_count([('active', '=', True)])
        
    #     # Get counts by state
    #     states = ['new', 'in_use', 'repair', 'retired']
    #     by_status = {}
        
    #     for state in states:
    #         count = self.search_count([('state', '=', state), ('active', '=', True)])
    #         if count > 0:
    #             by_status[state] = count
        
    #     return {
    #         'total': total,
    #         'by_status': by_status
    #     }

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

    @api.depends('component_id.capacity')
    def _compute_total_ram_gb(self):
        for rec in self:
            capacity = rec.component_id.capacity
            if capacity:
                rec.total_ram_gb += capacity

    @api.depends('component_id.disk_size')
    def _compute_total_storage_gb(self):
        for rec in self:
            disk_size = rec.component_id.disk_size
            if disk_size:
                rec.total_storage_gb += disk_size

    @api.model_create_multi
    def create(self, vals_list):
        computers = super().create(vals_list)
        for computer in computers:
            # subscribe employees when equipment assign to him.
            partner_ids = []
            for employee in computer.employee_ids:
                if employee.user_id:
                    partner_ids.append(employee.user_id.partner_id.id)
            if partner_ids:
                computer.message_subscribe(partner_ids=partner_ids)
        return computers

    def write(self, vals):
        partner_ids = []
        # subscribe employees when equipment assign to him.
        if vals.get('employee_ids'):
            employees = self.env['ict.employee'].browse(vals['employee_ids'])
            for employee in employees:
                if employee.user_id:
                    partner_ids.append(employee.user_id.parent_id.id)
        if partner_ids:
            self.message_subscribe(partner_ids=partner_ids)
        return super(ICTComputer, self).write(vals)