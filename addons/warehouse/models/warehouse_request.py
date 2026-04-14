# -*- coding: utf-8 -*-

from odoo import api
from odoo.models import Model
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.fields import Char, Text, Date, Many2one, Float, One2many, Boolean
from datetime import datetime


class WarehouseRequest(Model):
    _name = 'warehouse.warehouse_request'
    _description = 'warehouse.warehouse_request'
    _rec_name = 'code'

    code = Char(required=True)
    date = Date(readonly=False, default= lambda self: Date.context_today(self))

    warehouse_id = Many2one('warehouse.warehouse', string='Warehouse', required=True)
    applicant_id = Many2one('hr.employee', string='Applicant')
    driver_id = Many2one('warehouse.employee_driver', string='Solicita')
    employee = Boolean(string=u'Es un empleado?')
    authorize_id = Many2one('hr.employee', string='Authorize', required=True, domain=[('can_authorize_a_request', '=', True)])
    receive_id = Many2one('hr.employee', string='Receive')

    requested_product_ids = One2many('warehouse.product_order', inverse_name='warehouse_request_id', string='Products')
    note = Text()

    @api.multi
    def unlink(self):
        for record in self:
            record.requested_product_ids.unlink()
        return super(WarehouseRequest, self).unlink()

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        new_args = []
        for arg in args:
            if arg[0] == 'requested_product_ids':
                products = self.env['simple_product.product'].search(
                    ['|', ('name', arg[1], arg[2]), ('code', arg[1], arg[2])]
                )

                product_orders = self.env['warehouse.product_order'].search(
                    [('product_id', 'in', [x.id for x in products])]
                )

                new_args.append(['requested_product_ids', 'in', [x.id for x in product_orders]])
            else:
                new_args.append(arg)

        return super(WarehouseRequest, self).search(new_args, offset=offset, limit=limit, order=order, count=count)
WarehouseRequest()


class ProductOrder(Model):
    _name = 'warehouse.product_order'
    _description = 'warehouse.product_order'

    def _default_warehouse(self):
        return self.env.context.get('warehouse_id', False)

    @api.constrains('quantity')
    def _check_product_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_('The requested product quantity must be great than 0.0...'))

    warehouse_request_id = Many2one('warehouse.warehouse_request', ondelete='cascade')
    warehouse_id = Many2one('warehouse.warehouse', string='Warehouse', required=True, default=_default_warehouse)
    product_id = Many2one('simple_product.product', string='Product', required=True)
    quantity = Float(digits=(16, 4), required=True)

    @api.one
    def _compute_shelf(self):
        for location in self.product_id.location_ids:
            if location.warehouse_id.id == self.warehouse_id.id:
                loc = location.location.split('-')
                self.shelf = loc[2] if len(loc) >= 3 else ''

    @api.one
    def _compute_row(self):
        for location in self.product_id.location_ids:
            if location.warehouse_id.id == self.warehouse_id.id:
                loc = location.location.split('-')
                self.row = loc[3] if len(loc) >= 4 else ''

    @api.one
    def _compute_pigeonhole(self):
        for location in self.product_id.location_ids:
            if location.warehouse_id.id == self.warehouse_id.id:
                loc = location.location.split('-')
                self.pigeonhole = loc[4] if len(loc) >= 5 else ''

    shelf = Char(compute=_compute_shelf)
    row = Char(compute=_compute_row)
    pigeonhole = Char(compute=_compute_pigeonhole)

    @api.one
    def _compute_request_date(self):
        self.request_date = self.warehouse_request_id.date

    request_date = Date(compute=_compute_request_date)
ProductOrder()
