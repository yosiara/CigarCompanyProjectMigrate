# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2012-2015 Odoo Desoft Solutions Suite (<http://odoo.hlg.desoft.cu>).
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

from odoo import models, fields, api
from odoo.tools.translate import _

class Locals(models.Model):
    
    _name = 'l10n_cu_locals.local'
    _description = "Physical structure that belongs to the company."
    _order = 'ext,code'

    # COLUMNS--------------------------
    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=10, help='The Local code in 10 chars.', required=True)
    parent_id = fields.Many2one('l10n_cu_locals.local', 'Parent Local', index=True)
    child_ids = fields.One2many('l10n_cu_locals.local', 'parent_id', 'Child Locals')
    employee_ids = fields.One2many('hr.employee', 'local_id', 'Employees')
    employee_list = fields.Char('Employees', help='Employees list',)
    ext = fields.Char('Ext.', size=7, help='The Local extension in 3 numbers.')

    _sql_constraints = [('local_code_uniq', 'unique(code)', _("The local code must be unique."))]

    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        lista = ''
        for emp in self.employee_ids:
            lista = emp.name+', '+lista
        self.employee_list=lista


class Employee(models.Model):

    _inherit = "hr.employee"

    local_id = fields.Many2one('l10n_cu_locals.local', string='Current Local', help='Employee locals work.', ondelete='set null')

    @api.onchange('local_id')
    def onchange_local(self):
        self.work_location=self.local_id.name
        self.mobile_phone = self.local_id.ext

    def write(self, vals):
        if 'local_id' in vals:
            local = self.env['l10n_cu_locals.local'].browse(vals['local_id'])
            if local:
                vals['work_location'] = local.name
                vals['mobile_phone'] = local.ext
            else:
                vals['work_location'] = ''
                vals['mobile_phone'] = ''
        return super(Employee, self).write(vals)

    # def unlink(self):
    #     print self
    #     return super(Employee, self).unlink()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
