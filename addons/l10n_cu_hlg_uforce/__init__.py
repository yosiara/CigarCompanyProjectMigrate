# -*- coding: utf-8 -*-

import models
import wizards
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    data = env['l10n_cu_base.reg'].search([('name', '=', 'l10n_cu_hlg_uforce')])
    if len(data) == 0:
        env['l10n_cu_base.reg'].create({'name': 'l10n_cu_hlg_uforce'})

    module = env['ir.module.module'].search([('name', '=', 'base_import')])
    if module.state == 'installed':
        module.write({'state': 'to remove'})

