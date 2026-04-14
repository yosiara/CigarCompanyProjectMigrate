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


class ContractToExpire(models.TransientModel):
    _name = "l10n_cu_contract.to_expire"

    today = datetime.today().date()
    today = today.replace(day=1)

    date = today + relativedelta(months=1)
    date_end = (date + timedelta(days=-1))
    uno = today.strftime('%d-%m-%Y') + " al " + date_end.strftime('%d-%m-%Y')

    date1 = today + relativedelta(months=2)
    date_end1 = (date1 + timedelta(days=-1))
    date_start = date_end + timedelta(days=1)
    dos = date_start.strftime('%d-%m-%Y') + " al " + date_end1.strftime('%d-%m-%Y')

    date2 = today + relativedelta(months=3)
    date_end2 = (date2 + timedelta(days=-1))
    date_start1 = date_end1 + timedelta(days=1)
    tres = date_start1.strftime('%d-%m-%Y') + " al " + date_end2.strftime('%d-%m-%Y')

    cuatro = today.strftime('%d-%m-%Y') + " al " + date_end2.strftime('%d-%m-%Y')

    flow = fields.Selection([
        ('customer', 'Sale'),
        ('supplier', 'Purchase'),
    ], 'Flow', required=True)

    type = fields.Selection(string="Formato", selection=[('xls', tools.ustr('EXCEL')),('doc', tools.ustr('DOC'))], required=True, default='xls')

    time = fields.Selection(string="Tiempo", selection=[('1', tools.ustr(uno)), ('2', tools.ustr(dos)), ('3', tools.ustr(tres)), ('4', tools.ustr(cuatro))], required=True, default='1')

    @api.multi
    def print_report(self):
        # resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_contract')
        # if resp != 'ok':
        #     raise ValidationError(resp_dic[resp])

        self.ensure_one()
        [data] = self.read()

        domain = [('state', 'in', ['open'])]
        if self.flow:
            domain.append(('flow', '=', self.flow))
        today = datetime.today().date()
        today = today.replace(day=1)
        date = today + relativedelta(months=1)
        date_end = (date + timedelta(days=-1))
        date1 = today + relativedelta(months=2)
        date_end1 = (date1 + timedelta(days=-1))
        day = ""
        if self.time == '1':
            domain.append(('date_end', '>=', today.strftime('%Y-%m-%d')))
            domain.append(('date_end', '<=', date_end.strftime('%Y-%m-%d')))
            day = tools.ustr(today.strftime('%d-%m-%Y') + " AL " + date_end.strftime('%d-%m-%Y'))

        elif self.time == '2':
            date_start = date_end + timedelta(days=1)
            domain.append(('date_end', '>=', date_start.strftime('%Y-%m-%d')))
            domain.append(('date_end', '<=', date_end1.strftime('%Y-%m-%d')))
            day = tools.ustr(date_start.strftime('%d-%m-%Y') + " AL " + date_end1.strftime('%d-%m-%Y'))

        elif self.time == '3':
            date2 = today + relativedelta(months=3)
            date_end2 = (date2 + timedelta(days=-1))
            date_start1 = date_end1 + timedelta(days=1)
            domain.append(('date_end', '>=', date_start1.strftime('%Y-%m-%d')))
            domain.append(('date_end', '<=', date_end2.strftime('%Y-%m-%d')))
            day = tools.ustr(date_start1.strftime('%d-%m-%Y') + " AL " + date_end2.strftime('%d-%m-%Y'))

        else:
            date2 = today + relativedelta(months=3)
            date_end2 = (date2 + timedelta(days=-1))
            domain.append(('date_end', '>=', today.strftime('%Y-%m-%d')))
            domain.append(('date_end', '<=', date_end2.strftime('%Y-%m-%d')))
            day = tools.ustr(today.strftime('%d-%m-%Y') + " AL " + date_end2.strftime('%d-%m-%Y'))


        contract_list = self.env['l10n_cu_contract.contract'].search(domain)
        contract_ids = self.env['l10n_cu_contract.contract'].search(domain).mapped('id')

        if self.type == 'doc':
            list_contract = []
            datas = {}
            for c in contract_list:
                contract = {}
                contract['archive_nro'] = c.partner_id.archive_nro
                contract['number'] = c.number
                contract['name'] = c.partner_id.name
                contract['denominacion'] = c.name
                contract['amount_total'] = c.amount_total
                contract['date_start'] = c.date_start
                contract['date_end'] = c.date_end
                date_end = datetime.strptime(c.date_end, '%Y-%m-%d')
                today = datetime.today()
                contract['days_end'] = (date_end - today).days
                contract['employee'] = c.employee_id.name

                list_contract.append(contract)

            datas['list_contract'] = list_contract
            datas['time'] = day
            return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'l10n_cu_hlg_contract.contract_to_expire_doc_report',
                        'datas': datas,
                    }

        return self.env['report'].get_action(self, 'l10n_cu_hlg_contract.contract_to_expire_xls_report', data={
            'flow': tools.ustr(self.flow, 'utf-8'),
            'ids': contract_ids,
            'time': self.time,
        })