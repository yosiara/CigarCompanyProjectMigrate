# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return

        part = self.invoice_id.partner_id
        fpos = self.invoice_id.fiscal_position_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type

        if not part:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a partner!'),
            }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id

            self.name = product.partner_ref
            account = self.get_invoice_line_account(type, product, fpos, company)
            if account:
                self.account_id = account.id
            self._set_taxes()

            if type in ('in_invoice', 'in_refund'):
                if product.description_purchase:
                    self.name += '\n' + product.description_purchase
            else:
                if product.description_sale:
                    self.name += '\n' + product.description_sale

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if company and currency:
                if company.currency_id != currency:
                    self.price_unit = self.price_unit * currency.with_context(
                        dict(self._context or {}, date=self.invoice_id.date_invoice)).rate

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)

                self.price_unit_cuc = product.list_price_cuc
                self.price_unit = product.list_price
        return {'domain': domain}

class ContractLines(models.Model):
    _inherit = "l10n_cu_contract.contract_lines"

    price_cuc = fields.Float(string='Price CUC', required=True, digits=dp.get_precision('Product Price'))
    amount_cuc = fields.Monetary(string='Amount CUC', compute='_amount_line_cuc')

    @api.one
    @api.depends('quantity', 'price_cuc')
    def _amount_line_cuc(self):
        self.amount_cuc = self.price_cuc * self.quantity

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.price = self.product_id.list_price
            self.price_cuc = self.product_id.list_price_cuc


class Contract(models.Model):
    _inherit = "l10n_cu_contract.contract"

    invoice_cup = fields.Monetary(string='Invoice CUP', compute='_invoice_cup', store=True)
    invoice_cuc = fields.Monetary(string='Invoice CUC', compute='_invoice_cuc', store=True)
    total_cup = fields.Monetary(string='Amount CUP', compute='_amount_cup', store=True)
    total_cuc = fields.Monetary(string='Amount CUC', compute='_amount_cuc', store=True)

    @api.one
    @api.depends('invoice_cup', 'invoice_cuc')
    def _amount_invoice(self):
        self.amount_invoice = self.invoice_cup + self.invoice_cuc

    @api.one
    @api.depends('line_ids')
    def _amount_cup(self):
        amount = 0
        for line in self.line_ids:
            amount += line.amount
        self.total_cup = amount

    @api.one
    @api.depends('line_ids')
    def _amount_cuc(self):
        amount_cuc = 0
        for line in self.line_ids:
            amount_cuc += line.amount_cuc
        self.total_cuc = amount_cuc

    @api.one
    @api.depends('invoice_ids', 'child_ids')
    def _invoice_cup(self):
        total = 0
        for invoice in self.invoice_ids:
            if invoice.state != 'cancel':
                total += invoice.amount_total_cup
        for contract in self.child_ids:
            if contract.update_lines:
                total += contract.invoice_cup
        self.invoice_cup = total

    @api.one
    @api.depends('invoice_ids', 'child_ids')
    def _invoice_cuc(self):
        total = 0
        for invoice in self.invoice_ids:
            if invoice.state != 'cancel':
                total += invoice.amount_total_cuc
        for contract in self.child_ids:
            if contract.update_lines:
                total += contract.invoice_cuc
        self.invoice_cuc = total

    @api.one
    @api.depends('line_ids')
    def _amount_total(self):
        total = 0
        for line in self.line_ids:
            total += (line.amount + line.amount_cuc)
        self.amount_total = total

    @api.one
    def set_open(self):
        if not self.number:
            raise UserError(_("Error! Number in contract empty."))
        if self.date_end < fields.Datetime.now() and not self.hco:
            raise UserError(_("Error! End date must be greater than actual date."))
        if self.update_date:
            self.parent_id.date_end = self.date_end
        if self.update_lines:
            if self.option_select == 'add':
                array = []

                for line in self.line_ids:
                    dicc = {}
                    dicc['contract_id'] = self.parent_id.id
                    dicc['price'] = line.price
                    dicc['price_cuc'] = line.price_cuc
                    dicc['quantity'] = line.quantity
                    dicc['currency_id'] = line.currency_id.id
                    dicc['product_id'] = line.product_id.id
                    array.append((0, 0, dicc))
                self.parent_id.line_ids = array
            elif self.option_select == 'update_quantity':
                array = []
                self.parent_id.line_ids = [(5, 0, 0)]
                for line in self.line_ids:
                    dicc = {}
                    dicc['contract_id'] = self.parent_id.id
                    dicc['price'] = line.price
                    dicc['price_cuc'] = line.price_cuc
                    dicc['quantity'] = line.quantity
                    dicc['currency_id'] = line.currency_id.id
                    dicc['product_id'] = line.product_id.id
                    array.append((0, 0, dicc))
                self.parent_id.line_ids = array

        if self.required_milestone_payment:
            if not self.milestone_payment_ids:
                raise UserError(_("I need some milestone payments!"))
            else:
                sale_order_obj = self.env['sale.order']
                for payment in self.milestone_payment_ids:
                    array = []
                    for line in payment.line_ids.lines_milestone_payment:
                        quantity = line.amount_payment / line.contract_lines_ids.price
                        data_sale_order_line = dict(name='Prueba', invoice_status='to invoice',
                                                    product_id=line.contract_lines_ids.product_id.id,
                                                    price_unit=line.contract_lines_ids.price,
                                                    product_uom_qty=quantity,
                                                    product_uom=line.contract_lines_ids.product_id.uom_id.id,
                                                    )
                        array.append((0, 0, data_sale_order_line))
                    data_sale_order = dict(partner_id=self.partner_id.id, partner_invoice_id=self.partner_id.id,
                                           partner_shipping_id=self.partner_id.id,
                                           pricelist_id=self.env.ref('product.list0').id,
                                           order_line=array,
                                           origin=self.number,
                                           contract_id=self.id,
                                           external_create=True)
                    sale_order_obj.create(data_sale_order)
        self.state = 'open'


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        _ids = super(AccountInvoice, self).create(vals)
        _ids.contract_id._compute_percentage_execution()
        _ids.contract_id._amount_cup()
        _ids.contract_id._amount_cuc()
        _ids.contract_id._invoice_cup()
        _ids.contract_id._invoice_cuc()
        _ids.contract_id._amount_total()
        _ids.contract_id._amount_invoice()
        _ids.contract_id._amount_rest()
        return _ids

    @api.multi
    def write(self, vals):
        contract = self.contract_id
        if 'contract_id' in vals:
            _ids = super(AccountInvoice, self).write(vals)
            _ids.contract_id._compute_percentage_execution()
            _ids.contract_id._amount_cup()
            _ids.contract_id._amount_cuc()
            _ids.contract_id._invoice_cup()
            _ids.contract_id._invoice_cuc()
            _ids.contract_id._amount_total()
            _ids.contract_id._amount_invoice()
            _ids.contract_id._amount_rest()
        else:
            _ids = super(AccountInvoice, self).write(vals)
            contract._compute_percentage_execution()
            contract._amount_cup()
            contract._amount_cuc()
            contract._invoice_cup()
            contract._invoice_cuc()
            contract._amount_total()
            contract._amount_invoice()
            contract._amount_rest()
        return _ids

    @api.multi
    def unlink(self):
        contract = self.env['l10n_cu_contract.contract'].search([('id', '=', self.contract_id.id)])
        if len(contract) > 0:
            contract._compute_percentage_execution()
            contract._amount_cup()
            contract._amount_cuc()
            contract._invoice_cup()
            contract._invoice_cuc()
            contract._amount_total()
            contract._amount_invoice()
            contract._amount_rest()
        return super(AccountInvoice, self).unlink()