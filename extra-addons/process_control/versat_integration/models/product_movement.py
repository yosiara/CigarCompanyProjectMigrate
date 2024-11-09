# -*- coding: utf-8 -*-

from odoo import api
from odoo.models import Model
from odoo.tools.translate import _
from odoo.fields import Many2one, Integer, Float, Selection, Date, Char


class ProductMovement(Model):
    """ Used to manage de product transference... """

    _name = 'versat_integration.product_movement'
    _description = 'versat_integration.product_movement'

    external_id = Integer(required=True)
    product_id = Many2one('simple_product.product', string='Product', required=True)
    quantity = Float(digits=(16, 4), required=True)

    warehouse_id = Many2one('warehouse.warehouse', string='Warehouse', required=True)
    type = Selection([('in', _('In')), ('out', _('Out'))], required=True)
    movement_concept = Integer(string='Movement concept')
    description = Char()
    date = Date()

    @api.multi
    def unlink(self):
        product_control_obj = self.env['warehouse.product_control']
        for product_movement in self:
            product_control = product_control_obj.search(
                [('warehouse_id', '=', product_movement.warehouse_id.id),
                 ('product_id', '=', product_movement.product_id.id)], limit=1
            )

            if len(product_control):
                if product_movement.type == 'in':
                    quantity_system = product_control[0].quantity_system - product_movement.quantity
                    quantity = product_control[0].quantity - product_movement.quantity

                elif product_movement.type == 'out':
                    quantity_system = product_control[0].quantity_system + product_movement.quantity
                    quantity = product_control[0].quantity + product_movement.quantity

                product_control.write({
                    'quantity': quantity,
                    'quantity_system': quantity_system
                })

        super(ProductMovement, self).unlink()
ProductMovement()
