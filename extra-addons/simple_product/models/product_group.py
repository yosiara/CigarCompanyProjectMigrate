# -*- coding: utf-8 -*-

from odoo.fields import Char, Text
from odoo.models import Model


class ProductGroup(Model):
    _name = 'simple_product.product.group'
    _description = 'simple_product.product.group'

    code = Char(index=True, required=True)
    name = Char(required=True)
    description = Text(placekolder='A description of the product group...')
ProductGroup()
