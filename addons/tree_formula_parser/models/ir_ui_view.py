# -*- coding: utf-8 -*-
from odoo import models, api, fields


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(
        selection_add=[('tree_formula_parser', "Tree formula Parser")])
