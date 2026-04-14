# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployeeConfiguration(models.TransientModel):
    _name = 'hr.employee.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.user.company_id
    )

    module_l10n_cu_hlg_hr_driving_license = fields.Boolean("Manage driving license per employee")
    module_l10n_cu_hlg_hr_travels = fields.Boolean("Manage Employee Travels")
    module_l10n_cu_hlg_hr_uniforms = fields.Boolean("Manage Employee uniforms")
