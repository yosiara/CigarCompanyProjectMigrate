# -*- coding: utf-8 -*-

from odoo import api, models, fields


class Account(models.Model):
    _name = 'versat_integration.account'
    _description = 'versat_integration.account'

    @api.multi
    def name_get(self):
        return [(x.id, '%s - %s' % (x.code, x.name)) for x in self]

    code = fields.Integer(required=True)
    name = fields.Char(required=True)
    external_id = fields.Integer()
