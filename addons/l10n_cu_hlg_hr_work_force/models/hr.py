# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from datetime import datetime


class Employee(models.Model):
    _inherit = 'hr.employee'

    degree_id = fields.Many2one('l10n_cu_hlg_hr_work_force.degree', string='Degree')
    # fields required for XML to GFORZA
    contract_hr_type_id = fields.Many2one('l10n_cu_hlg_hr_work_force.contract_hr_type', string='Contract HR Type')
    age_range_id = fields.Many2one('l10n_cu_hlg_hr_work_force.age_range', store=True,
                                   compute='_compute_age_range', string='Age Range from Gforza', ondelete='set null')
    first_name = fields.Char(string='First name')
    last_name = fields.Char(string='Last name')
    second_last_name = fields.Char(string='Second last name')

    @api.depends('age', 'gender', 'birthday')
    @api.one
    def _compute_age_range(self):
        age_range_obj = self.env['l10n_cu_hlg_hr_work_force.age_range']

        if self.age != 0:
            if self.age < 31:
                age_range_id = age_range_obj.search([('code', '=', '2920')], limit=1).id
                self.age_range_id = age_range_id
            elif 31 <= self.age <= 50:
                age_range_id = age_range_obj.search([('code', '=', '2921')], limit=1).id
                self.age_range_id = age_range_id
            elif 51 <= self.age <= 60:
                age_range_id = age_range_obj.search([('code', '=', '2922')], limit=1).id
                self.age_range_id = age_range_id
            elif self.age >= 60:
                age_range_id = age_range_obj.search([('code', '=', '2923')], limit=1).id
                self.age_range_id = age_range_id

    @api.one
    @api.constrains('name')
    def _check__name(self):
        valid_name_regexp = "^([ a-zA-ZáéíóúñÑÁÉÍÓÚÀÈÌÒÙàèìòùü'.,\-])+$"

        if self.name:
            assert re.match(valid_name_regexp, self.name.encode('utf8')), 'Name has numbers'


class SupplementMotive(models.Model):
    _inherit = 'hr_contract.supplement_motive'

    code = fields.Char(string='Code')


# ADD fron Gforza Integration
class ContractHrType(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.contract_hr_type'
    _description = 'Employee Contract HR Type'

    code = fields.Char()
    name = fields.Char(required=True)
    external_id = fields.Char()
