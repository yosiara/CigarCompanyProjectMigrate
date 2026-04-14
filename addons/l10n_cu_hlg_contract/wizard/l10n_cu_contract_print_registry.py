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

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError
import pytz
from datetime import datetime

resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.')}


class ContractPrintRegistry(models.TransientModel):
    _name = "l10n_cu_contract.print_registry"

    flow = fields.Selection([
        ('customer', 'Sale'),
        ('supplier', 'Purchase'),
    ], 'Flow', required=True)

    type = fields.Selection(string="Format", selection=[('pdf', tools.ustr('PDF')), ('xls', tools.ustr('EXCEL')),('doc', tools.ustr('DOC')), ], required=True, default='pdf')
    state = fields.Selection([('draft', 'New'),
                              ('pending_dict', 'Pending Dict.'),
                              ('pending_appro', 'Pending Appro.'),
                              ('rejected', 'Rejected'),
                              ('approval', 'Approved'),
                              ('pending_signed', 'Pending Signed'),
                              ('open', 'In Action'),
                              ('close', 'Closed'),
                              ('cancelled', 'Cancelled')],
                             'Status', required=False,
                             track_visibility='onchange', default='open')
    date_start = fields.Date('Start Date', required=False)
    date_end = fields.Date('End Date', required=False)

    @api.multi
    def print_report(self):
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.ensure_one()
        [data] = self.read()
        domain = []
        if self.state:
            domain.append(('state', '=', self.state))
        if self.date_start and self.date_end:
            domain.append(('date_start', '>=', self.date_start))
            domain.append(('date_start', '<=', self.date_end))
        if self.flow:
            domain.append(('flow', '=', self.flow))

        contract_ids = self.env['l10n_cu_contract.contract'].search(domain).mapped('id')
        contract_obj_ids = self.env['l10n_cu_contract.contract'].search(domain)
        datas = {
            'ids': contract_ids,
            'model': 'l10n_cu_contract.contract',
            'form': data,
            'flow': tools.ustr(self.flow, 'utf-8'),
        }
        if self.type == 'pdf':
            return self.env['report'].get_action(self, 'l10n_cu_hlg_contract.report_contract_template', data=datas)
        if self.type == 'xls':
            # return self.env['report'].get_action(self, 'l10n_cu_hlg_contract.contract_single_xls_report', data=datas)
            datas = {
                'flow': tools.ustr(self.flow, 'utf-8'),
                'state': self.state,
                'date_start': self.date_start,
                'date_end': self.date_end,
            }
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_hlg_contract.contract_single_xls_report.xlsx',
                'datas': datas,
                'name': 'Reporte de contratos'
            }

        list_contract = []
        datas = {}
        for c in contract_obj_ids:
            contract = {}
            contract['archive_nro'] = c.partner_id.archive_nro
            contract['number'] = c.number
            contract['partner'] = c.partner_id.name
            contract['name'] = c.name
            contract['amount'] = "{0:.2f}".format(c.amount_total).replace('.', ',')
            if c.flow == 'customer':
                contract['flow'] = 'Cliente'
            else:
                contract['flow'] = 'Proveedor'

            contract['date_start'] = c.date_start
            contract['date_end'] = c.date_end
            contract['employee'] = c.employee_id.name
            list_contract.append(contract)

        datas['list_contract'] = list_contract
        datas['flow'] = 'VENTAS' if self.flow == 'customer' else 'COMPRAS'
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_contract.contract_single_doc_report',
                    'datas': datas,
                }

