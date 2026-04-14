# -*- coding: utf-8 -*-
from lxml import etree

from odoo.exceptions import ValidationError
from odoo.http import addons_manifest
from odoo import models
from odoo.tools.translate import _

resp_dic = {'nokey': _('You must request a registry key. Please contact the support center for a new one.'),
            'invalidkey': _('You are using a invalid key. Please contact the support center for a new one.'),
            'expkey': _('You are using a expired key. Please contact the support center for a new one.'),
            'invalidmod': _('You are using a invalid key. Please contact the support center for a new one.')}


class UpdateEmployeeAgeRange(models.TransientModel):
    _name = 'l10n_cu_hlg_uforce.update_employee_age_range_wzd'

    def update_employee_age_range(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        employee_reg = self.env['hr.employee'].search([])
        age_range_obj = self.env['l10n_cu_hlg_uforce.age_range']

        for rec in employee_reg:
            if rec.age < 31:
                age_range_id = age_range_obj.search([('code', '=', '2920')], limit=1).id
                rec.write({'age_range_id': age_range_id})
            elif 31 <= rec.age <= 50:
                age_range_id = age_range_obj.search([('code', '=', '2921')], limit=1).id
                rec.write({'age_range_id': age_range_id})
            elif 51 <= rec.age <= 60:
                age_range_id = age_range_obj.search([('code', '=', '2922')], limit=1).id
                rec.write({'age_range_id': age_range_id})
            elif rec.age >= 60:
                age_range_id = age_range_obj.search([('code', '=', '2923')], limit=1).id
                rec.write({'age_range_id': age_range_id})

        return True
