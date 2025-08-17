# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo import modules, tools
from odoo.fields import Char, Text, Binary, One2many


class Warehouse(Model):
    """ This class was created whit the purpose to give us an alternative to the original
        warehouse's module of Odoo, and don't force us to control the accountancy.... """

    _name = 'warehouse.warehouse'
    _description = 'warehouse.warehouse'

    def _get_default_image(self):
        img_path = modules.get_module_resource('warehouse', 'static/img/default.png')
        with open(img_path, 'rb') as f:
            image = f.read()
        return tools.image_resize_image_big(image.encode('base64'))

    code = Char(required=True)
    name = Char(required=True)
    description = Text('Description')
    image = Binary(default=_get_default_image)

    # Inventory...
    product_control_ids = One2many('warehouse.product_control', inverse_name='warehouse_id', string='Products...')
Warehouse()
