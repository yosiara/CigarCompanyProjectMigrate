# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ProductGroup(models.Model):
    _name = 'simple_product.product_group'
    _description = 'Product Group'

    code = fields.Char('Code', index=True, required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text(placeholder='A description of the product group...')