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


from odoo import models, fields, api


class RegistryInformation(models.TransientModel):
    _name = "l10n_cu_hlg_computers_inventory.registry_information"

    def _get_seed(self):
        return self.env['l10n_cu_base.reg'].get_seed('l10n_cu_hlg_computers_inventory')

    def _get_key(self):
        return self.env['l10n_cu_base.reg'].get_key('l10n_cu_hlg_computers_inventory')

    def _get_days(self):
        return self.env['l10n_cu_base.reg'].get_days('l10n_cu_hlg_computers_inventory')

    def _get_reg(self):
        status=self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_computers_inventory')
        if status in ('invalidkey','invalidmod'):
            return 'unreg'
        if status == 'nokey':
            return 'sinclave'
        if status == 'expkey':
            return 'exp'
        if status == 'ok':
            return 'reg'

    seed = fields.Char('Seed', readonly=True, default=_get_seed)
    key = fields.Char('Key', default=_get_key)
    state = fields.Selection([('unreg', 'Unregistered'), ('reg', 'Registered'), ('exp', 'Expired'),('sinclave', 'Sin clave')], default=_get_reg, string='UEB Desoft',)
    days_left = fields.Integer('Days left', default=_get_days, readonly=True)

    def save_key(self):
        return self.env['l10n_cu_base.reg'].save_key('l10n_cu_hlg_computers_inventory', self.key)