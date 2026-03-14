# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ICTComputer(models.Model):
    _name = 'ict.computer'
    _description = 'Computer Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name/Serial Number', required=True, tracking=True)
    type = fields.Selection([
        ('desktop', 'Desktop'),
        ('laptop', 'Laptop'),
        ('server', 'Server'),
    ], string='Type', required=True, default='desktop')
    
    brand = fields.Char(string='Brand', required=True)
    model = fields.Char(string='Model', required=True)
    processor = fields.Char(string='Processor')
    ram_gb = fields.Integer(string='RAM (GB)')
    # total_ram_gb = fields.Integer(string='Total RAM (GB)', compute='_compute_total_ram_gb')
    storage_gb = fields.Integer(string='Storage (GB)')
    # total_storage_gb = fields.Integer(string=_('Total Storage (GB)'), compute='_compute_total_storage_gb')
    storage_type = fields.Selection([
        ('hdd', 'HDD'),
        ('ssd', 'SSD'),
        ('nvme', 'NVMe'),
    ], string='Storage Type')
    
    operating_system = fields.Selection([
        ('windows_10', 'Windows 10'),
        ('windows_11', 'Windows 11'),
        ('windows_server', 'Windows Server'),
        ('linux', 'Linux'),
        ('macos', 'macOS'),
    ], string='Operating System')
    
    ip_address = fields.Char(string='IP Address')
    mac_address = fields.Char(string='MAC Address')
    
    employee_id = fields.Many2one('ict.employee', string='Assigned to')
    employee_name = fields.Char(related='employee_id.name')
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True)
    department_name = fields.Char(string=_('Department name'), related="department_id.name")

    purchase_date = fields.Date(string='Purchase Date')
    warranty_date = fields.Date(string='Warranty End Date')
    supplier = fields.Char(string='Supplier')
    state = fields.Selection([
        ('new', 'New'),
        ('in_use', 'In Use'),
        ('repair', 'Under Repair'),
        ('retired', 'Retired'),
    ], string='Status', default='new')
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

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

    # @api.depends('ram_ids')
    # def _compute_total_ram_gb(self):
    #     for rec in self:
    #         total = 0
    #         for ram in rec.ram_ids:
    #             total += ram.size
    #         rec.total_ram_gb = total