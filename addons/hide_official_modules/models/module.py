# -*- coding: utf-8 -*-

from odoo import api
from odoo.models import Model


class Module(Model):
    _inherit = 'ir.module.module'

    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     if self.env.context.get('search_default_app', False):
    #         args += [
    #             '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
    #             ('author', 'ilike', 'Alejandro Cora González'), ('author', 'ilike', 'Desoft. Holguín. Cuba.'),
    #             ('name', '=', 'hr'), ('name', '=', 'web_export_view'), ('name', '=', 'backend_theme_v10'),
    #             ('name', '=', 'base'), ('name', '=', 'product'), ('name', '=', 'decimal_precision'),
    #             ('name', '=', 'mail'), ('name', '=', 'report'), ('name', '=', 'base_setup'),
    #             ('name', '=', 'web'), ('name', '=', 'bus'), ('name', '=', 'web_tour'),
    #             ('name', '=', 'web_kanban'), ('name', '=', 'resource')
    #         ]
    #
    #     return super(Module, self).search(args, offset=offset, limit=limit, order=order, count=count)
Module()
