# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ReportsWzd(models.TransientModel):
    _name = 'reports.wzd'

    type = fields.Selection([('l10n_cu_hlg_hr_contract.employee_register', 'Company Job Position (A.14)'),
                             ('l10n_cu_hlg_hr_contract.by_employee_register', 'Job Positions by Employee (A.14B)'),
                             ('l10n_cu_hlg_hr_contract.by_category_register', 'Company Category-Job Position (A.14-A)'),
                             ('l10n_cu_hlg_hr_contract.approved_template', 'Approved template'),
                             ('l10n_cu_hlg_hr_contract.vacancies', 'Vacancies'),
                             ('l10n_cu_hlg_hr_contract.approved_cover', 'Approved template and cover'),
                             ('l10n_cu_hlg_hr_contract.current_situation', 'Current situation of the workforce'),
                             ('l10n_cu_hlg_hr_contract.vacancies_total', 'Vacancies total'),
                             ('l10n_cu_hlg_hr_contract.covered_by_categories', 'Template summary Covered by categories'),
                             ('l10n_cu_hlg_hr_contract.qualified_workforce', 'Qualified workforce')
                            ],
                             'Reportes', required=True,
                             default='l10n_cu_hlg_hr_contract.employee_register')

    @api.multi
    def print_report(self):
        datas = {}

        return self.env['report'].get_action([], self.type, data=datas)
