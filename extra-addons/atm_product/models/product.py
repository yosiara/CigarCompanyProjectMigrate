# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Boolean, Char, Integer, Many2one


class Product(Model):
    _inherit = 'simple_product.product'

    is_protected = Boolean(string='Is protected?')
    is_tool_or_util = Boolean(string='Is util or tool?')
    is_for_contingency = Boolean(string='Is for contingency?')
    do_not_use = Boolean(string='Must it not be used?')
    is_exclusive_product = Boolean(string='Exclusive?', help='Checked if the product if for exclusive use of a area...')

    owner_id = Many2one('hr.employee', string='Owner')
    protection_cause = Char(placeholder='Cause of the product protection...')
    contingency_quantity = Integer(string='Quantity', help='Quantity that must be kept for contingencies...')
    area_id = Many2one('l10n_cu_base.area', string='Area')
