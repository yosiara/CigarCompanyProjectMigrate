from odoo import api
from odoo.models import Model
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.fields import Char, Text, Date, Many2one, Float, One2many, Boolean
from datetime import datetime

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

    
    def _compute_shelf(self):
        for location in self.product_id.location_ids:
            if location.warehouse_id.id == self.warehouse_id.id:
                loc = location.location.split('-')
                self.shelf = loc[2] if len(loc) >= 3 else ''

    
    def _compute_row(self):
        for location in self.product_id.location_ids:
            if location.warehouse_id.id == self.warehouse_id.id:
                loc = location.location.split('-')
                self.row = loc[3] if len(loc) >= 4 else ''

    
    def _compute_pigeonhole(self):
        for location in self.product_id.location_ids:
            if location.warehouse_id.id == self.warehouse_id.id:
                loc = location.location.split('-')
                self.pigeonhole = loc[4] if len(loc) >= 5 else ''

    shelf = Char(compute=_compute_shelf)
    row = Char(compute=_compute_row)
    pigeonhole = Char(compute=_compute_pigeonhole)

    
    def _compute_request_date(self):
        self.request_date = self.warehouse_request_id.date

    request_date = Date(compute=_compute_request_date)