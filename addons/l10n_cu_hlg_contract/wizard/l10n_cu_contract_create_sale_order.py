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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.')}


class CreateSaleOrder(models.TransientModel):
    _name = "l10n_cu_contract.create_sale_order"

    @api.multi
    def create_sale_order(self):
        sale_order_obj = self.env['sale.order']
        contracts = self.env['l10n_cu_contract.contract'].search([('state', '=', 'open'), ('date_start', '>=', '01-01-2019')])
        for contract in contracts:
            for payment in contract.milestone_payment_ids:
                array = []
                for line in payment.line_ids.lines_milestone_payment:
                    quantity = line.amount_payment / line.contract_lines_ids.price
                    data_sale_order_line = dict(name=line.contract_lines_ids.product_id.name,
                                                invoice_status='to invoice',
                                                product_id=line.contract_lines_ids.product_id.id,
                                                price_unit=line.contract_lines_ids.price,
                                                product_uom_qty=quantity,
                                                product_uom=line.contract_lines_ids.product_id.uom_id.id,
                                                )
                    array.append((0, 0, data_sale_order_line))
                data_sale_order = dict(partner_id=contract.partner_id.id,
                                       partner_invoice_id=contract.partner_id.id,
                                       partner_shipping_id=contract.partner_id.id,
                                       pricelist_id=contract.env.ref('product.list0').id,
                                       order_line=array,
                                       origin=contract.number,
                                       contract_id=contract.id,
                                       external_create=True,
                                       date_order=payment.date,
                                       user_id=contract.employee_id.user_id.id,
                                       department_id=contract.department_id.id,
                                       )
                sale_order_obj.create(data_sale_order)
                self.env.cr.commit()
