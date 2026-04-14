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

resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.')}


class ContractPrintRegistry(models.TransientModel):
    _name = "l10n_cu_contract.print_template"

    contract_id = fields.Many2one('l10n_cu_contract.contract', 'Contract', required=True,
                                 track_visibility='onchange',)


    @api.multi
    def print_report(self):
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.ensure_one()
        [data] = self.read()

        contract_ids = self.env['l10n_cu_contract.contract'].search([('id', '=', self.contract_id.id)])

        #for c in contract_ids:

        datas = {
            'name': contract_ids.partner_id.name
        }
        print datas


        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_contract.contract_print_template_report',
                    'datas': datas,
                }