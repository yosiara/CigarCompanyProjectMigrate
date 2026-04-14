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

import logging

_logger = logging.getLogger(__name__)
from odoo import models, api, fields


class GroupAddEmployeeWzd(models.TransientModel):
    _name = "l10n_cu_calendar.group_add_employee_wzd"

    # COLUMNS
    employee_ids = fields.Many2many('hr.employee', 'l10n_cu_calendar_group_add_employee_wzd_employee_rel', 'group_add_employee_wzd_id', 'employee_id', 'Employees', required=True)
    group_ids = fields.Many2many('l10n_cu_calendar.org_group', 'l10n_cu_calendar_group_add_employee_wzd_group_rel', 'group_add_employee_wzd_id', 'group_id', 'Groups', required=True)
    include_in_group_tasks = fields.Boolean('Include in groups tasks', default=True, required=True)
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    # -------

    @api.one
    def execute(self):
        for employee in self.employee_ids:
            if employee.user_id:
                for group in self.group_ids:
                    group.partner_group_ids |= employee.user_id.partner_id

                if self.include_in_group_tasks:
                    groups = self.env['l10n_cu_calendar.org_group'].search([('partner_group_ids', 'in', [employee.user_id.partner_id.id])])
                    events = self.env['calendar.event'].search([('start', '>=', self.date_start), ('start', '<=', self.date_end), ('attendees_group_ids', 'in', groups.ids)])
                    for event in events:
                        event.partner_ids |= employee.user_id.partner_id

        return True
