# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models

class ProductControl(models.Model):
    """ To manage the product stock... """

    _name = 'warehouse.product_control'
    _description = 'Product Control'

    warehouse_id = fields.Many2one('warehouse.warehouse', string='Warehouse')
    product_id = fields.Many2one('simple_product.product', 'Product', required=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', store=True)

    quantity = fields.Float(required=True, digits=(16, 4))
    quantity_system = fields.Float(digits=(16, 4), help='Maybe will be used for validation purpose...')