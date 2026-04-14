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
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.')}


class ContractToExpirePercent(models.TransientModel):
    _name = "l10n_cu_contract.to_expire_percent"

    @api.model
    def _default_percent(self):
        percentage = self.env['ir.config_parameter'].sudo().get_param('contract_monetary')
        if not percentage:
            percentage = 75
        return percentage

    percent = fields.Float(string='Percent', required=True, default=_default_percent)
    flow = fields.Selection([
        ('customer', 'Sale'),
        ('supplier', 'Purchase'),
    ], 'Flow', required=True)
    type = fields.Selection(string="Format", selection=[('pdf', tools.ustr('PDF')), ('xls', tools.ustr('EXCEL')),
                                                        ('doc', tools.ustr('DOC')), ], required=True, default='pdf')

    @api.multi
    def print_report(self):
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])
        data = {
            'percent': self.percent,
            'flow': self.flow
        }
        if self.type == 'pdf':
            return self.env['report'].get_action(self, 'l10n_cu_hlg_contract.report_contract_to_expire_percent', data=data)
        elif self.type == 'xls':
            datas = {
                'flow': tools.ustr(self.flow, 'utf-8'),
                'percent': self.percent,
            }
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_hlg_contract.contract_single_xls_percent_report.xlsx',
                'datas': datas,
                'name': 'Contratos'
            }
        else:
            domain = []
            if self.percent:
                domain.append(('percentage_execution', '>=', self.percent))
            if self.flow:
                domain.append(('flow', '=', self.flow))
            list_contract = []
            datas = {}
            contract_obj_ids = self.env['l10n_cu_contract.contract'].search(domain, order='percentage_execution DESC')
            for c in contract_obj_ids:
                contract = {}
                contract['number'] = c.number
                contract['partner'] = c.partner_id.name
                contract['name'] = c.name
                contract['amount'] = "{0:.2f}".format(c.amount_total).replace('.', ',')
                contract['invoice'] = "{0:.2f}".format(c.amount_invoice).replace('.', ',')
                contract['rest'] = "{0:.2f}".format(c.amount_rest).replace('.', ',')
                contract['por'] = "{0:.2f}".format(c.percentage_execution).replace('.', ',')
                contract['date_start'] = c.date_start
                contract['date_end'] = c.date_end
                list_contract.append(contract)

            datas['list_contract'] = list_contract
            datas['por_ciento'] = "{0:.2f}".format(self.percent).replace('.', ',')
            datas['flow'] = 'ventas' if self.flow == 'customer' else 'compras'
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_hlg_contract.contract_single_doc_percent_report',
                'datas': datas,
            }

