# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ICTComputer(models.Model):
    _name = 'ict.computer'
    _description = 'ICT Computer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'maintenance.equipment': 'equipment_id'}

    equipment_id = fields.Many2one('maintenance.equipment', string='Related Equipment', required=True,
        ondelete='cascade', auto_join=True, index=True, help='Equipment-related data of the computer')

    # Equipment fields
    # name = fields.Char('Equipment Name', required=True, translate=True)
    # active = fields.Boolean(default=True)
    # owner_user_id = fields.Many2one('res.users', string='Owner', tracking=True)
    # category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category',
    #                               tracking=True, group_expand='_read_group_category_ids')
    # partner_id = fields.Many2one('res.partner', string='Vendor', check_company=True)
    # partner_ref = fields.Char('Vendor Reference')
    # location = fields.Char('Location')
    # model = fields.Char('Model')
    # serial_no = fields.Char('Serial Number', copy=False)
    # assign_date = fields.Date('Assigned Date', tracking=True)
    # cost = fields.Float('Cost')
    # note = fields.Html('Note')
    # warranty_date = fields.Date('Warranty Expiration Date')
    # color = fields.Integer('Color Index')
    # scrap_date = fields.Date('Scrap Date')
    # maintenance_ids = fields.One2many('maintenance.request', 'equipment_id')
    # equipment_properties = fields.Properties('Properties', definition='category_id.equipment_properties_definition', copy=True)
    # match_serial = fields.Boolean(compute='_compute_match_serial')

    # computer_id = fields.One2many(comodel_name='ict.computer', inverse_name='equipment_id', string='ICT Computer')

    pc_type = fields.Selection([
        ('desktop', 'Desktop'),
        ('laptop', 'Laptop'),
        ('server', 'Server'),
    ], string='Type', required=True, default='desktop')

    brand = fields.Char(string='Brand', required=True)
    purchase_date = fields.Date(string='Purchase Date')
    state = fields.Selection([
        ('new', 'New'),
        ('in_use', 'In Use'),
        ('repair', 'Under Repair'),
        ('retired', 'Retired'),
    ], string='Status', default='new')
    
    employee_ids = fields.Many2many('ict.employee', 'ict_computer_employees_rel', 'computer_id', 'employee_id', 'Assigned Employees')
    responsible_name = fields.Char(string='Responsible', compute='_compute_responsible', store=True,
                                    help=_("The first employee selected will be considered the team's top manager."))
    inventory_number = fields.Char('Inventory Number')
    seal = fields.Char('Seal')
    ocs_external_id = fields.Integer(index=True)
    is_a_computer = fields.Boolean('Is an ICT equipment?', default=True)

    component_ids  = fields.One2many('ict.computer.component', 'computer_id', 'Components', domain=[('is_active', '=', True)])
    application_ids = fields.One2many('ict.computer.application', 'computer_id', 'Applications')

    processor_name = fields.Char(string='Processor', compute='_compute_component', store=True)
    total_memory_gb = fields.Integer(string='Total Memory (GB)', compute='_compute_component', store=True)
    total_storage_gb = fields.Integer(string='Total Storage (GB)', compute='_compute_component', store=True)

    operating_system = fields.Selection([
        ('windows_10', 'Windows 10'),
        ('windows_11', 'Windows 11'),
        ('windows_server', 'Windows Server'),
        ('linux', 'Linux'),
        ('macos', 'macOS'),
    ], string='Operating System')
    os_version = fields.Char()
    ip_address = fields.Char(string='IP Address')
    mac_address = fields.Char(string='MAC Address')
    uuid = fields.Char()
    architecture = fields.Char()
    domain = fields.Char()

    # qrcode_image = fields.Binary("QRCode", compute='get_qrimage')

    # To know the state in the importation...
    # 1 -> Imported.
    # 2 -> Updated first time.
    # 3 -> Updated more than once time.
    # importation_state = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')], default='1')
    # information_updated_date = fields.Datetime()

    _sql_constraints = [
        ('equipment_id', 'unique(equipment_id)', "Related equipment already exists!"),
    ]

    @api.onchange('equipment_assign_to')
    def _onchange_equipment_assign_to(self):
        if self.equipment_assign_to == 'department':
            self.employee_ids = False

    @api.depends('employee_ids')
    def _compute_responsible(self):
        for pc in self:
            if pc.employee_ids:
                responsible = pc.employee_ids[0]
                pc.employee_id = responsible
                if responsible.name != pc.responsible_name:
                    pc.responsible_name = responsible.name
            else:
                pc.employee_id = False
                pc.responsible_name = False

    @api.depends('component_ids')
    def _compute_component(self):
        for pc in self:
            total_memory  = 0
            total_storage = 0
            micro = self.env['ict.computer.component']

            for component in pc.component_ids:
                type_ = component.component_type
                if type_ == 'processor':
                    micro |= component
                elif type_ == 'memory':
                    total_memory += component.capacity
                elif type_ == 'storage':
                    total_storage += component.disk_size
            
            pc.processor_name   = micro[0].name if micro else False
            pc.total_memory_gb  = total_memory
            pc.total_storage_gb = total_storage

    # Get methods
    def get_component(self, component_type):
        return self.component_ids.filtered_domain([('component_type', '=', component_type)])
    def ups(self):
        return self.get_component('ups')
    def fax(self):
        return self.get_component('fax')
    def modem(self):
        return self.get_component('modem')
    def board(self):
        return self.get_component('board')
    def memory(self):
        return self.get_component('memory')
    def scanner(self):
        return self.get_component('scanner')
    def speaker(self):
        return self.get_component('speaker')
    def storage(self):
        return self.get_component('storage')
    def monitor(self):
        return self.get_component('monitor')
    def printer(self):
        return self.get_component('printer')
    def processor(self):
        return self.get_component('processor')
    def video_card(self):
        return self.get_component('video_card')
    def sound_card(self):
        return self.get_component('sound_card')
    def input_device(self):
        return self.get_component('input_device')
    def power_source(self):
        return self.get_component('power_source')
    
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
            employees = self.env['ict.employee'].browse([t[1] for t in vals['employee_ids']])
            for employee in employees:
                if employee.user_id:
                    partner_ids.append(employee.user_id.partner_id.id)
        if partner_ids:
            self.message_subscribe(partner_ids=partner_ids)
        return super(ICTComputer, self).write(vals)

    def action_change_state(self):
        # Abre un wizard para cambiar estado con motivo
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'change.computer.state.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_computer_id': self.id}
        }
    
    def action_retire(self):
        self.state = 'retired'
        self.scrap_date = fields.Date.today()

    def action_start_using(self):
        self.state = 'in_use'

    def action_send_repair(self):
        self.state = 'repair'

    def action_retire(self):
        self.state = 'retired'
        self.scrap_date = fields.Date.today()