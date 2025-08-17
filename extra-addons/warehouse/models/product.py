# -*- coding: utf-8 -*-

from odoo import api
from odoo.models import Model
from odoo.fields import One2many, Char, Many2one


class Product(Model):
    _inherit = "simple_product.product"

    
    def _compute_product_controls_as_str(self):
        rep = ""
        cont = 1
        for x in self.product_control_ids:
            rep += x.warehouse_id.code + ': ' + str(x.quantity)
            if not len(self.product_control_ids) == cont:
                rep += ', '
            cont += 1
        self.product_control_str = rep

    product_control_ids = One2many('warehouse.product_control', inverse_name='product_id', string='Stock')
    product_control_str = Char(compute='_compute_product_controls_as_str')

    # Useful because a product can be stored in some warehouses...
    location_ids = One2many('warehouse.product.location', inverse_name='product_id', string='Locations...')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        warehouse_id = self.env.context.get('warehouse_id', False)
        if not warehouse_id and self.env.context.get('only_products_from_warehouse', False):
            return []

        args = args or []
        product_ids = []

        if warehouse_id and self.env.context.get('only_products_from_warehouse', False):
            ctrl_obj = self.env['warehouse.product_control']
            ctrls = ctrl_obj.search([('warehouse_id', '=', warehouse_id), ('quantity', '>', 0.0)])
            product_ids = [ctrl.product_id.id for ctrl in ctrls]

        if name:
            args = ['|', ('code', operator, name), ('name', operator, name)] + args

        if warehouse_id and self.env.context.get('only_products_from_warehouse', False):
            args = [('id', 'in', product_ids)] + args

        return self.search(args, limit=limit).name_get()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        model_id = self.env.context.get('object_id')
        if model_id:
            model = self.env['ir.model'].browse(model_id).model
            args.append(('model', '=', model))

        return super(Product, self).search(args, offset=offset, limit=limit, order=order, count=count)
Product()


class ProductLocation(Model):
    _name = 'warehouse.product.location'
    _description = 'warehouse.product.location'

    warehouse_id = Many2one('warehouse.warehouse', string='Warehouse')
    product_id = Many2one('simple_product.product', string='Product')
    location = Char()
ProductLocation()
