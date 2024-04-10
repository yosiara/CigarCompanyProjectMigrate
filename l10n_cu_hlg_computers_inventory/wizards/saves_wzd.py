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


from odoo import models, fields, api


class Saves(models.TransientModel):
    _name = "computers_inventory.saves_wzd"

    elaborates_id = fields.Many2one('hr.employee', 'Elaborates', required=True)
    approved_id = fields.Many2one('hr.employee', 'Approved', required=True)
    format = fields.Selection([('pdf', 'PDF'), ('docx', 'DOCX')], 'Format', default='pdf', required=True)

    #@api.multi
    def print_report(self):
        data = {}
        data['elaborates_id'] = self.elaborates_id.id
        data['approved_id'] = self.approved_id.id

        if self.format == 'pdf':
            return self.env['report'].get_action(self, 'l10n_cu_hlg_computers_inventory.report_saves', data=data)
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_hlg_computers_inventory.report_saves_docx',
                'datas': data
            }