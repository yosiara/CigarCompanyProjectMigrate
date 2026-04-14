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


class HiringStatus(models.TransientModel):
    _name = "l10n_cu_contract.hiring_status"

    date_end = fields.Date('End Date', required=False)

    @api.multi
    def print_report(self):
        # resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_contract')
        # if resp != 'ok':
        #     raise ValidationError(resp_dic[resp])

        self.ensure_one()
        [data] = self.read()

        datas = {
            'date_end': self.date_end,
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'l10n_cu_hlg_contract.contract_hiring_status_xls_report.xlsx',
            'datas': datas,
            'name': 'Estado Contratacion x Organismos'
        }
