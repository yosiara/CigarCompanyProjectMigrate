# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp

AVAILABLE_PRIORITIES = [
    ('sale', 'Sale'),
    ('purchase', 'Purchase'),
]


class CrmTeam(models.Model):
    _inherit = "crm.team"

    type = fields.Selection(AVAILABLE_PRIORITIES, 'Type')
    legal = fields.Boolean('Legal', default=False)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    list_price = fields.Float(
        'Sale Price', default=0,
        digits=dp.get_precision('Product Price'),
        help="Base price to compute the customer price. Sometimes called the catalog price.")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    contract_id = fields.Many2one('l10n_cu_contract.contract', 'Contract')
    external_create = fields.Boolean('External Create', default=False)
    department_id = fields.Many2one('hr.department', 'Department', track_visibility='onchange')

    @api.multi
    def unlink(self):
        # for order in self:
        #     if order.external_create:
        #         raise UserError(_('You can not delete a sales order with external create!'))
        return super(SaleOrder, self).unlink()

    @api.constrains('order_line')
    def _check_order_line(self):
        if self.order_line:
            if self.contract_id:
                if self.contract_id.contract_type.check_lines:
                    a = self.contract_id.line_ids.mapped('product_id')
                    for line in self.order_line:
                        if line.product_id not in a:
                            raise UserError(_('Error! Product %s not permitted.') % line.product_id.name)
        return True

    @api.multi
    def _prepare_invoice(self):
        dicc = super(SaleOrder, self)._prepare_invoice()
        dicc['contract_id'] = self.contract_id.id
        dicc['external_create'] = self.external_create
        return dicc


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         args = args or []
#         domain = []
#         if self._context.get('contract'):
#             contract = self.env['l10n_cu_contract.contract'].search([('id', '=', self._context['contract'])])
#             product_ids = contract.line_ids.mapped('product_id')
#             if len(product_ids) > 0:
#                 args += ([('id', 'in', product_ids.ids)])
#         obj = self.search(domain + args, limit=limit)
#         return obj.name_get()



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    contract_id = fields.Many2one('l10n_cu_contract.contract', 'Contract')
    external_create = fields.Boolean('External Create', default=False)
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='always')


    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        self.contract_id = False
        return res

    @api.constrains('invoice_line_ids')
    def _check(self):
        if self.contract_id.contract_type.check_lines:
            product_lines_contract = self.contract_id.line_ids.mapped('product_id')
            for line in self.invoice_line_ids:
                if line.product_id not in product_lines_contract:
                    raise ValidationError(_('Error! Product %s not permitted.') % line.product_id.name)

        if self.contract_id.contract_type.check_quantity_lines:
            for product in self.contract_id.line_ids:
                qty = 0
                for invoice in self.contract_id.invoice_ids:
                    if invoice.state in ['draft', 'open', 'paid']:
                        for line in invoice.invoice_line_ids:
                            if line.product_id == product.product_id:
                                qty += line.quantity
                if qty > product.quantity:
                    raise ValidationError(_('Error! Product %s quantity not permitted.') % product.product_id.name)

        if self.contract_id.contract_type.check_general_amount:
            if not self.contract_id.amount_bool:
                if self.contract_id.amount_total < self.contract_id.amount_invoice:
                    raise ValidationError(_('Error! Amount not permitted.'))

    @api.model
    def create(self, vals):
        _ids = super(AccountInvoice, self).create(vals)
        _ids.contract_id._compute_percentage_execution()
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
            _ids.contract_id._amount_total()
            _ids.contract_id._amount_invoice()
            _ids.contract_id._amount_rest()
        else:
            _ids = super(AccountInvoice, self).write(vals)
            contract._compute_percentage_execution()
            contract._amount_total()
            contract._amount_invoice()
            contract._amount_rest()
        return _ids

    @api.multi
    def unlink(self):
        contract = self.env['l10n_cu_contract.contract'].search([('id', '=', self.contract_id.id)])
        if len(contract) > 0:
            contract._compute_percentage_execution()
            contract._amount_total()
            contract._amount_invoice()
            contract._amount_rest()
        return super(AccountInvoice, self).unlink()

