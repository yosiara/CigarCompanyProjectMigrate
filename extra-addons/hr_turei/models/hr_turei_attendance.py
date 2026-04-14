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
from odoo import tools, api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class hr_turei_attendance_reason_type(models.Model):
    _name = 'hr_turei.attendance_reason_type'
    _description = u"Incidence´s Reason"

    name = fields.Char('Reason', required=True)
    code = fields.Char('Code', required=True)


class hr_turei_attendance_reason(models.Model):
    _name = 'hr_turei.attendance_reason'
    _description = u"Incidence´s Reason"

    name = fields.Char('Reason', required=True, help='Specifies the reason for Signing In/Signing Out.')
    code = fields.Char('Code', required=True, help='Specifies the code for Signing In/Signing Out.')
    type = fields.Many2one('hr_turei.attendance_reason_type', 'Type', index=True)


class hr_turei_attendance_incidence(models.Model):
    _name = 'hr_turei.attendance_incidence'
    _description = "Employee work time Incidences"
    _order = 'date desc'
    _rec_name = 'employee_id'

    def _compute_date(self):
        for issue in self:
            values = {
                'day_date': 0,
                'month_date': "",
                'year_date': 0
            }

            if issue.fecha:
                day_s = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
                values['day_date'] = day_s[datetime.weekday(datetime.strptime(issue.fecha, '%Y-%m-%d'))]
            issue.day_date = values['day_date']

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get()
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    employee_id = fields.Many2one('hr.employee', 'Employee', index=True)
    employee_code = fields.Char(related='employee_id.code', string='Code', store=True)
    date = fields.Date('Date', readonly=True, default=fields.Date.today)
    employee_turn = fields.Char('Employee shift', help='Employee shift in fastos.')
    employee_turn_order = fields.Integer('Employee shift order', help='Employee shift order in fastos.')
    entry_date = fields.Datetime('Entry Date')
    exit_date = fields.Datetime('Exit Date')
    working_time = fields.Float('Working time')
    not_working_time = fields.Float('Not working time')
    reason_id = fields.Many2one('hr_turei.attendance_reason', 'Reason', index=True)
    reason_code = fields.Char(related='reason_id.code', string='Code', store=True)

    def name_get(self):
        res = []
        for record in self.read(['date', 'employee_code']):
            name = record['employee_code'] + ' / ' + record['date']
            res.append((record['id'], name))
        return res
