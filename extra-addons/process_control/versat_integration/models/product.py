# -*- coding: utf-8 -*-

from odoo import api
from odoo.models import Model
from odoo.fields import Integer, One2many, Float, Many2one


class ProductProduct(Model):
    _inherit = 'simple_product.product'

    @api.one
    def _compute_quantity_by_movements_in(self):
        cant = 0.0
        for mov in self.movement_in_ids:
            cant += mov.quantity
        self.quantity_by_movements_in = cant

    @api.one
    def _compute_quantity_by_movements_out(self):
        cant = 0.0
        for mov in self.movement_out_ids:
            cant += mov.quantity
        self.quantity_by_movements_out = cant

    @api.one
    def _compute_quantity_by_out_requests(self):
        cant = 0.0
        for mov in self.out_request_ids:
            cant += mov.quantity
        self.quantity_by_out_requests = cant

    @api.one
    def _compute_total(self):
        self.total = self.quantity_by_movements_in - self.quantity_by_movements_out - self.quantity_by_out_requests

    external_id = Integer()
    account_id = Many2one('versat_integration.account', string='Account')
    out_request_ids = One2many('warehouse.product_order', inverse_name='product_id', string='Out requests')

    movement_in_ids = One2many(
        'versat_integration.product_movement', inverse_name='product_id', string='Movements in',
        domain=[('type', '=', 'in')]
    )

    movement_out_ids = One2many(
        'versat_integration.product_movement', inverse_name='product_id', string='Movements out',
        domain=[('type', '=', 'out')]
    )

    quantity_by_movements_in = Float(compute=_compute_quantity_by_movements_in)
    quantity_by_movements_out = Float(compute=_compute_quantity_by_movements_out)
    quantity_by_out_requests = Float(compute=_compute_quantity_by_out_requests)
    total = Float(compute=_compute_total)

    _sql_constraints = [
        ('unique_external_id', 'unique(external_id)', 'The external identifier must be unique!'),
    ]


class ProductCategory(Model):
    _inherit = 'product.category'

    external_id = Integer()

    _sql_constraints = [
        ('unique_external_id', 'unique(external_id)', 'The external identifier must be unique!'),
    ]
