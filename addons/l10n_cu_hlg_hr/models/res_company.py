# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api


class Company(models.Model):
    _inherit = "res.company"

    reeup_code = fields.Char(related='partner_id.reeup_code', string='REEUP code', store=True)
    nit_code = fields.Char(related='partner_id.nit_code', string='NIT Code', store=True)
