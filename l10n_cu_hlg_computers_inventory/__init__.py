# -*- coding: utf-8 -*-

import models
import wizards
import reports
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    data = env['l10n_cu_base.reg'].search(
        [('name', '=', 'l10n_cu_hlg_computers_inventory')])
    if len(data) == 0:
        env['l10n_cu_base.reg'].create({
            'name': 'l10n_cu_hlg_computers_inventory'
        })