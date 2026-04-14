# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class WorkOrder(models.Model):
    _inherit = 'computers_inventory.work_order'

    cost_center = fields.Many2one('l10n_cu_base.cost_center', string='Cost Center')
