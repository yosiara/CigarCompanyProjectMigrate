# -*- coding: utf-8 -*-

from odoo import api, tools
from odoo.models import Model
from odoo.fields import Char, Boolean, Binary, Float, Text, Many2one, Integer


class Product(Model):
    _name = 'simple_product.product'
    _description = 'simple_product.product'

    @api.one
    def _get_default_uom_id(self):
        return self.env["product.uom"].search([], limit=1, order='id').id

    @api.one
    def _get_default_category_id(self):
        if self._context.get('category_id') or self._context.get('default_category_id'):
            return self._context.get('category_id') or self._context.get('default_category_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        return category and category.id or False

    code = Char(index=True, required=True)
    name = Char(required=True)

    image = Binary(
        "Big-sized image",
        help="Image of the product variant (Big-sized image of product template if false). It is automatically "
             "resized as a 1024x1024px image, with aspect ratio preserved.")

    image_small = Binary(
        "Small-sized image",
        help="Image of the product variant (Small-sized image of product template if false).")

    image_medium = Binary(
        "Medium-sized image",
        help="Image of the product variant (Medium-sized image of product template if false).")

    price = Float('Price', digits=(6, 4))
    price_extra = Float('Price CUC', digits=(6, 4))

    color = Integer('Color Index')
    active = Boolean(default=True, help="If unchecked, it will allow you to hide the product without removing it...")
    description = Text(translate=True, help="A precise description, used only for internal information purposes...")
    is_new = Boolean(string='Is new?', default=True)

    category_id = Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id, domain="[('type','=','normal')]",
        required=False, help="Select category for the current product")

    uom_id = Many2one(
        'product.uom', 'Unit of Measure',
        default=_get_default_uom_id, required=False,
        help="Default Unit of Measure used for all stock operation.")

    group_id = Many2one('simple_product.product.group', string='Product Group')

    @api.multi
    def name_get(self):
        return [(rec.id, '[%s] %s' % (rec.code, rec.name)) for rec in self]

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(Product, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(Product, self).write(vals)
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            args = ['|', ('code', operator, name), ('name', operator, name)] + args
        return self.search(args, limit=limit).name_get()

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The code must be unique!')
    ]
