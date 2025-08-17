# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Char, Text, Many2one, Datetime, Float, One2many, Integer
from odoo import fields
import pytz

class BlindReception(Model):
    _name = 'atm.blind_reception'
    _description = 'atm.blind_reception'
    _rec_name = 'code'

    def _get_code(self):
        work_orders = self.search([], limit=1, order='creation_date DESC, code DESC')
        if not len(work_orders):
            return '00001'

        temp = int(work_orders[0].code)
        rep = str(temp + 1)
        code = ''

        for x in range(0, 5 - len(rep)):
            code += '0'

        code += rep
        return code

    def get_datetime_now(self):
        for c_model in self:
            tz = pytz.timezone(self._context.get('tz') or 'UTC')
            date = pytz.UTC.localize(fields.Datetime.from_string(c_model.creation_date))
            date = date.astimezone(tz)            
        return fields.Datetime.to_string(date)

    invoice_number = Char(required=True)
    code = Char(required=True, default=_get_code)
    supplier_id = Many2one('res.partner', string='Supplier', required=True, domain=[('supplier', '=', True)])

    creation_date = Datetime(readonly=False, default=Datetime.now)
    warehouse_id = Many2one('warehouse.warehouse', string='Warehouse', required=True)
    product_ids = One2many('atm.blind_reception.product', inverse_name='blind_reception_id', string='Products')
    notes = Text()

    approve_id = Many2one('hr.employee', string='Authorize', required=True, domain=[('can_authorize_a_blind_reception', '=', True)])
    driver_id = Many2one('warehouse.employee_driver', string='Chofer', required=True)
    buyer_id = Many2one('hr.employee', string='Buyer', required=False)

    container_or_box = Char()
    car_plate = Char(required=True)


class BlindReceptionProduct(Model):
    _name = 'atm.blind_reception.product'
    _description = 'atm.blind_reception.product'
    _order = 'sequence'

    sequence = Integer(string='Sequence')
    product_description = Char(required=True)
    blind_reception_id = Many2one('atm.blind_reception')
    uom_id = Many2one('product.uom', 'Unit of Measure', required=True)
    quantity = Float(digits=(16, 4))
