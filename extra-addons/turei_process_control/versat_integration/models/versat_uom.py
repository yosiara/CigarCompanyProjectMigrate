# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Integer, Char, Many2one


class VersatUnitOfMeasure(Model):
    """ This class it's used to make the correct link to the unit of measure of the
        Versat system database... """

    _name = 'versat.uom'
    _description = 'versat.uom'

    external_id = Integer()
    name = Char(string='Code', required=True)
    uom_id = Many2one('product.uom', string='Reference uom')
    description = Char()
VersatUnitOfMeasure()
