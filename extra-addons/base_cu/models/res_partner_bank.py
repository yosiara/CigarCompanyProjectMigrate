# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'


    currency_name = fields.Char('Tipo Moneda',related='currency_id.name')

    def _default_name(self):
        if self._context.get('active_id'):
            partner = self.env['res.partner'].search([('id', '=', self._context['active_id'])])
            return partner.name

    name = fields.Char('Titular Name', required=True, default=_default_name)

