from odoo import api, fields, tools, models

class ProductLocation(models.Model):
    _name = 'warehouse.product_location'
    _description = 'Product Location'

    warehouse_id = fields.Many2one('warehouse.warehouse', string='Warehouse')
    product_id = fields.Many2one('simple_product.product', string='Product')
    location = fields.Char()