# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # ----------------------------- ATM Fields ---------------------------------- #
    has_assingments = fields.Boolean(string='Has assingments by area?')
    assingment_ids = fields.One2many('atm.product_assignment', inverse_name='product_id', string='Assingments...')
    protection_cause = fields.Char(placeholder='Cause of the product protection...')
    area_id = fields.Many2one('base_cu.area', string='Area')
    quantity_in_millions = fields.Float(string='Cantidad en MU')
    origin = fields.Selection([('national', 'Nacional'), ('international', 'Importación')], string='Procedencia')
    destiny_id = fields.Many2one('atm.product_destiny', string='Destino')
    # ----------------------------- ATM Fields ---------------------------------- #