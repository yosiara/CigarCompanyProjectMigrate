# -*- coding: utf-8 -*-

from odoo import api
from odoo.fields import Boolean
from odoo.models import Model


class Employee(Model):
    _inherit = 'hr.employee'
    can_authorize_a_blind_reception = Boolean(string='Can authorize a Blind Reception?')

    # @api.model_create_multi
    # def name_get(self):
    #     results = []
    #     for record in self:
    #         results.append((record.id, '[' + (record.employee_id_number or '') + '] ' + record.name))
    #     return results

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     if name:
    #         args = ['|', ('employee_id_number', '=', name),
    #                 '|', ('name', operator, name), ('identification_id', operator, name)] + args
    #
    #     ids = self.search(args, limit=limit)
    #     return ids.name_get()
Employee()
