# -*- coding: utf-8 -*-

from odoo import api
from odoo.exceptions import ValidationError
from odoo.fields import Float, Many2one
from odoo.tools.translate import _
from odoo.models import Model


class ProductOrder(Model):
    _inherit = 'warehouse.product_order'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            ctx = self._context
            ctrl_obj = self.env['warehouse.product_control']
            lst = ctrl_obj.search([('warehouse_id', '=', ctx['warehouse_id']), ('product_id', '=', self.product_id.id)])
            self.stock = lst[0].quantity if len(lst) else 0.0
            self.stock_validation = lst[0].quantity_system if len(lst) else 0.0
            self.uom_id = self.product_id.uom_id.id
        else:
            self.stock = 0.0
            self.stock_validation = 0.0

    stock = Float(digits=(16, 4), readonly=True, help='Product stock according to Versat...')
    stock_validation = Float(digits=(16, 4), readonly=True, help='Product stock according to the system...')
    uom_id = Many2one('uom.uom', 'Unit of Measure', readonly=True)

    @api.constrains('quantity')
    def _check_product_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_('The requested product quantity must be great than 0.0...'))

            if record.quantity > record.stock_validation:
                raise ValidationError(_('The requested product quantity can not be great than the product stock...'))

    @api.model
    def create(self, values):
        res = super(ProductOrder, self).create(values)

        control_obj = self.env['warehouse.product_control']
        controls = control_obj.search([('warehouse_id', '=', res.warehouse_request_id.warehouse_id.id),
                                       ('product_id', '=', values['product_id'])])

        if len(controls):
            controls.write({'quantity_system': controls[0].quantity_system - values['quantity']})
        return res

    @api.model_create_multi
    def write(self, values):
        if self.stock_validation < values.get('quantity'):
            raise ValidationError(_('The requested product quantity can not be great than the product stock...'))

        new_values = {}
        if values.get('quantity', False) and not values.get('product_id'):
            control_obj = self.env['warehouse.product_control']
            controls = control_obj.search([('warehouse_id', '=', self.warehouse_request_id.warehouse_id.id),
                                           ('product_id', '=', self.product_id.id)])

            if len(controls):
                if self.quantity > values['quantity']:
                    new_values['quantity_system'] = controls[0].quantity_system + abs(self.quantity - values['quantity'])
                if self.quantity < values['quantity']:
                    new_values['quantity_system'] = controls[0].quantity_system - abs(self.quantity - values['quantity'])
                controls.write(new_values)

        return super(ProductOrder, self).write(values)

    @api.model_create_multi
    def unlink(self):
        for record in self:
            control_obj = record.env['warehouse.product_control']
            controls = control_obj.search([('warehouse_id', '=', record.warehouse_request_id.warehouse_id.id),
                                           ('product_id', '=', record.product_id.id)])

            if len(controls):
                controls.write({'quantity_system': controls[0].quantity_system + record.quantity})

        return super(ProductOrder, self).unlink()
