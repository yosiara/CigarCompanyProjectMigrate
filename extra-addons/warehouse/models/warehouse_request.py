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

    @api.model_create_multi
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