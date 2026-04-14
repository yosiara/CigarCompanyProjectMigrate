# -*- coding: utf-8 -*-

from . import models
from . import wizards
from . import reports

# from odoo import api, SUPERUSER_ID

# def post_init_hook(cr, registry):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     data = env['base_cu.reg'].search(
#         [('name', '=', 'l10n_cu_hlg_computers_inventory')])
#     if len(data) == 0:
#         env['base_cu.reg'].create({
#             'name': 'l10n_cu_hlg_computers_inventory'
#        })