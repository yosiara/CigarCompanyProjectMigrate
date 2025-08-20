# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductOrder(models.Model):
    _name = 'maintenance_turei.product_order'
    _description = 'maintenance_turei.product_order'

    product_id = fields.Many2one('simple_product.product', string='Producto', required=True)
    quantity = fields.Float(digits=(16, 4), required=True, string='Cantidad')
    work_order_id = fields.Many2one(comodel_name="maintenance_turei.work_order", string="Documento",
                             required=False)