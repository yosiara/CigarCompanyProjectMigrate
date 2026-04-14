# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.'),
          'invalidmod':_('You are using a invalid key. Please contact the suport center for a new one.'),}

class RegistryInformation(models.TransientModel):
    _name = "l10n_cu_hlg_hr_contract.registry_information"

    def _get_seed(self):
        return self.env['l10n_cu_base.reg'].get_seed('l10n_cu_hlg_hr_contract')

    def _get_key(self):
        return self.env['l10n_cu_base.reg'].get_key('l10n_cu_hlg_hr_contract')

    def _get_days(self):
        return self.env['l10n_cu_base.reg'].get_days('l10n_cu_hlg_hr_contract')

    def _get_reg(self):
        status=self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if status in ('nokey','invalidkey','invalidmod'):
            return 'unreg'
        if status == 'expkey':
            return 'exp'
        if status == 'ok':
            return 'reg'

    seed = fields.Char('Seed', readonly=True, default=_get_seed)
    key = fields.Char('Key', default=_get_key)
    state = fields.Selection([('unreg', 'Unregistered'), ('reg', 'Registered'), ('exp', 'Expired')], default=_get_reg, string='UEB Desoft',)
    days_left = fields.Integer('Days left', default=_get_days, readonly=True)
    # days_percent=

    def save_key(self):
        return self.env['l10n_cu_base.reg'].save_key('l10n_cu_hlg_hr_contract',self.key)



