# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import models
import reports
import wizard
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    data = env['l10n_cu_base.reg'].search([('name', '=', 'l10n_cu_hlg_cmi')])
    if len(data) == 0:
        env['l10n_cu_base.reg'].create({'name': 'l10n_cu_hlg_cmi'})

    module = env['ir.module.module'].search([('name', '=', 'base_import')])
    if module.state == 'installed':
        module.write({'state': 'to remove'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
