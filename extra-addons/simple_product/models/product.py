# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class Product(models.Model):
    _name = 'simple_product.product'
    _description = 'Product'

    def _get_default_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order='id').id

    def _get_default_category_id(self):
        if self._context.get('category_id') or self._context.get('default_category_id'):
            return self._context.get('category_id') or self._context.get('default_category_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        return category and category.id or False

    code = fields.Char('Code', index=True, required=True)
    name = fields.Char('Name', required=True)

    image = fields.Binary(
        "Big-sized image",
        help="Image of the product variant (Big-sized image of product template if false). It is automatically "
             "resized as a 1024x1024px image, with aspect ratio preserved.")

    image_small = fields.Binary(
        "Small-sized image",
        help="Image of the product variant (Small-sized image of product template if false).")

    image_medium = fields.Binary(
        "Medium-sized image",
        help="Image of the product variant (Medium-sized image of product template if false).")

    price = fields.Float('Price', digits=(6, 4))
    price_extra = fields.Float('Price CUC', digits=(6, 4))

    color = fields.Integer('Color Index')
    active = fields.Boolean(default=True, help="If unchecked, it will allow you to hide the product without removing it...")
    description = fields.Text(translate=True, help="A precise description, used only for internal information purposes...")
    is_new = fields.Boolean(string='Is new?', default=True)

    category_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id, #domain="[('type','=','normal')]",
        required=False, help="Select category for the current product")

    uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        default=_get_default_uom_id, required=False,
        help="Default Unit of Measure used for all stock operation.")

    group_id = fields.Many2one('simple_product.product_group', string='Product Group')

    @api.model_create_multi
    def name_get(self):
        return [(rec.id, '[%s] %s' % (rec.code, rec.name)) for rec in self]

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(Product, self).create(vals)

    @api.model_create_multi
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
