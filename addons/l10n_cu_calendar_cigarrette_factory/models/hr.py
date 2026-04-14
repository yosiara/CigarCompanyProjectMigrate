# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models
from odoo.tools.translate import _


class Employee(models.Model):
    _inherit = 'hr.employee'
        
    # COLUMNS--------------------------
    visible = fields.Boolean('Visible', compute='_compute_visible')
    address_id = fields.Many2one('res.partner', string='Working Address', domain=[('supplier', '=', False),
                                                                                  ('customer', '=', False),
                                                                                  ('employee', '=', False),
                                                                                  ('is_company', '=', False)])
    address_home_id = fields.Many2one('res.partner', string='Home Address', domain=[('supplier', '=', False),
                                                                                    ('customer', '=', False),
                                                                                    ('employee', '=', False),
                                                                                    ('is_company', '=', False)])
    # END COLUMNS--------------------------

    @api.multi
    def _compute_visible(self):
        uid=self._uid
        model_config = self.env['res.groups'].fields_get()
        if model_config['name']['translate']:
            group_name = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Calendar Manager')
        else:
            group_name = _('Calendar Manager')

        groups = self.env['res.groups'].search([('name', '=', group_name)])
        calendar_manager = False
        for u in groups.users:
            if u.id == self._uid:
                calendar_manager = True

        for emp in self:
            if emp.user_id and (emp.user_id.id == uid or emp.parent_id.user_id.id == uid or emp.parent_id.parent_id.user_id.id == uid or calendar_manager):
                emp.visible = True



    #Abrir calendar del employee
    @api.multi
    def view_calendar(self):
        domain = []
        partner_id = self.env['hr.employee'].search([('id', '=', self._ids[0])]).user_id.partner_id.id
        if partner_id:
            domain = [('partner_ids', 'in', [partner_id])]

        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'calendar.event',
            'view_type': 'form',
            'view_mode': 'calendar,tree,form',
            'target': 'current',
            # 'context': {"mymeetings": 1},
            'domain': domain,
            'nodestroy': True
        }

    @api.model
    def create(self, vals):
        synchronize = True if any(elem in vals for elem in ['job_id', 'user_id', 'parent_id', 'department_id', 'work_email']) else False
        emp = super(Employee, self).create(vals)
        if synchronize:
            emp._update_partner()
        return emp

    @api.multi
    def write(self, vals):
        synchronize = True if any(elem in vals for elem in ['job_id', 'user_id', 'parent_id', 'department_id', 'work_email']) else False
        old_user_id = {}
        if 'user_id' in vals:
            for emp in self:
                old_user_id[emp.id] = emp.user_id

        employees = super(Employee, self).write(vals)
        if synchronize and employees:
            for emp in self:
                emp._update_partner(old_user_id)

        return employees

    def _update_partner(self, old_user_id={}):
        if self.user_id:
            partner = self.env['res.partner'].browse(self.user_id.partner_id.id)
            partner.write({'employee': True,
                           'customer': False,
                           'function': self.job_id.name if self.job_id else _('Not Definido'),
                           'boss_id': self.parent_id.user_id.partner_id.id if self.parent_id and self.parent_id.user_id else False,
                           'department_id': self.department_id.id if self.department_id else False,
                           'email': self.work_email,
                           'notify_email': 'always',
                           'user_id': self.user_id.id
                           })

        if self.id in old_user_id and old_user_id[self.id].user_id and old_user_id[self.id].user_id.id is not self.user_id.id:
            count = self.env['hr.employee'].search_count([('user_id', '=', old_user_id[self.id].user_id.id)])
            if count == 0:
                partner = self.env['res.partner'].browse(old_user_id[self.id].user_id.partner_id.id)
                partner.write({'employee': False})
