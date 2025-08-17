# -*- coding: utf-8 -*-

import datetime
from odoo import api
from odoo.fields import Float, Many2one, One2many, Boolean, Date
from odoo.models import Model


class ProductAssingment(Model):
    _name = 'atmsys.product_assignment'
    _description = 'atmsys.product_assignment'
    _rec_name = 'area_id'

    @api.one
    def _compute_given_quantity(self):
        request_obj = self.env['warehouse.warehouse_request']
        requests = request_obj.search([('area_id', '=', self.area_id.id)])

        first_day_current_year = datetime.datetime.now().strftime('%Y-01-01')
        last_day_current_year = datetime.datetime.now().strftime('%Y-12-31')
        requests = requests.filtered(lambda rec: first_day_current_year <= rec.date <= last_day_current_year)

        res = 0.0
        for request in requests:
            for requested_product in request.requested_product_ids:
                if requested_product.product_id.id == self.product_id.id:
                    res += requested_product.quantity

        self.given_quantity = res

    date = Date()
    area_id = Many2one('l10n_cu_base.area', string='Area', required=True)
    product_id = Many2one('simple_product.product', string='Product', required=True)
    given_quantity = Float(digits=(16, 4), compute=_compute_given_quantity)
    quantity = Float(digits=(16, 4), required=True)

    # To know the real request of the product...
    detail_ids = One2many('atmsys.product_assignment.detail', inverse_name='assingment_id', string='Deliveries...')

    @api.one
    def action_compute_product_deliveries(self):
        detail_obj = self.env['atmsys.product_assignment.detail']
        details = detail_obj.search([('assingment_id', '=', self.id)])
        details.unlink()

        first_day_current_year = datetime.datetime.now().strftime('%Y-01-01')
        last_day_current_year = datetime.datetime.now().strftime('%Y-12-31')

        request_obj = self.env['warehouse.warehouse_request']
        requests = request_obj.search([('area_id', '=', self.area_id.id), ('date', '>=', first_day_current_year),
                                       ('date', '<=', last_day_current_year)])

        lst = []
        for request in requests:
            for product_order in request.requested_product_ids:
                if product_order.product_id.id == self.product_id.id:
                    res = detail_obj.create({'date': request.date, 'quantity': product_order.quantity})
                    lst.append(res.id)

        self.detail_ids = lst
ProductAssingment()


class Product(Model):
    _inherit = 'simple_product.product'
    has_assingments = Boolean(string='Has assingments by area?')
    assingment_ids = One2many('atmsys.product_assignment', inverse_name='product_id', string='Assingments...')
Product()


class AssingmentDetail(Model):
    _name = 'atmsys.product_assignment.detail'
    _description = 'atmsys.product_assignment.detail'

    assingment_id = Many2one('atmsys.product_assignment')
    quantity = Float(digits=(16, 4))
    date = Date()
AssingmentDetail()
