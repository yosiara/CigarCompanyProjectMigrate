# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ICTReports(models.AbstractModel):
    _name = 'ict.reports'
    _description = 'ICT Reports and Statistics'

    @api.model
    def get_dashboard_stats(self):
        """Get statistics for the dashboard"""
        Employee = self.env['ict.employee']
        Computer = self.env['ict.computer']
        Phone = self.env['ict.phone']
        Service = self.env['ict.service']
        
        # General statistics
        stats = {
            'total_employees': Employee.search_count([('active', '=', True)]),
            'total_computers': Computer.search_count([('active', '=', True)]),
            'total_phones': Phone.search_count([('active', '=', True)]),
            'active_services': Service.search_count([('active', '=', True)]),
            'computers_by_state': [],
            'recent_assignments': []
        }
        
        # Computers by state
        states = ['new', 'in_use', 'repair', 'retired']
        for state in states:
            count = Computer.search_count([('state', '=', state), ('active', '=', True)])
            if count > 0:
                stats['computers_by_state'].append({
                    'state': state,
                    'count': count
                })
        
        # Recent assignments (last 5)
        recent_computers = Computer.search([
            ('employee_id', '!=', False)
        ], limit=5, order='write_date desc')
        
        for comp in recent_computers:
            stats['recent_assignments'].append({
                'id': comp.id,
                'employee': comp.employee_id.name,
                'equipment': f"{comp.brand} {comp.model} ({comp.name})",
                'date': comp.write_date.strftime('%d/%m/%Y') if comp.write_date else 'N/A'
            })
        
        return stats
