# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(
        selection_add=[('tree_formula_parser', "Tree formula Parser")])
