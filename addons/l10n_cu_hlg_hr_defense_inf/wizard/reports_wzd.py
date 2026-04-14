# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportsMylitaryWzd(models.TransientModel):
    _name = 'reports.militaty.wzd'

    type = fields.Selection(
        [('l10n_cu_hlg_hr_defense_inf.conciliation_military', 'Physical Conciliation of the Military Registry'),
         ('l10n_cu_hlg_hr_defense_inf.military_registry', 'Behavior of the Militaty Registry'),
         ('l10n_cu_hlg_hr_defense_inf.military_registry_list', 'Militaty Registry'),
         ('l10n_cu_hlg_hr_defense_inf.wear_template', 'Wear template'),
         ('l10n_cu_hlg_hr_defense_inf.invasion_template', 'Invasion template'),
         ],
        'Reportes', required=True,
        default='l10n_cu_hlg_hr_defense_inf.conciliation_military')

    @api.multi
    def print_report(self):
        datas = {}

        return self.env['report'].get_action([], self.type, data=datas)