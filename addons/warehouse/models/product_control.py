# -*- coding: utf-8 -*-

from odoo import api
from odoo.models import Model
from odoo.fields import Many2one, Float


class ProductControl(Model):
    """ To manage the product stock... """

    _name = 'warehouse.product_control'
    _description = 'warehouse.product_control'

    warehouse_id = Many2one('warehouse.warehouse', string='Warehouse')
    product_id = Many2one('simple_product.product', 'Product', required=True)
    uom_id = Many2one('product.uom', related='product_id.uom_id', store=True)

    quantity = Float(required=True, digits=(16, 4))
    quantity_system = Float(digits=(16, 4), help='Maybe will be used for validation purpose...')
ProductControl()
