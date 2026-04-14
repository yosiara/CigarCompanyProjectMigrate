# -*- coding:utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from datetime import timedelta, datetime, date
from odoo.tools.translate import _


class Organism(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.organism'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    ministry_id = fields.Many2one('l10n_cu.ministry', string='Ministry', required=True)


class CenterStudy(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.center_study'

    name = fields.Char('Name', size=150, required=True)
    initial_letters = fields.Char('Initial Letters', size=50)


class BranchScience(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.branch_science'

    code = fields.Char(required=True)
    name = fields.Char('Name', size=150, required=True)
    degree_level_id = fields.Many2one('l10n_cu_hlg_hr.employee_school_level', string='Degree Level')


class SpecialtyFamily(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.specialty_family'

    code = fields.Char(required=True)
    name = fields.Char('Name', size=150, required=True)
    degree_level_id = fields.Many2one('l10n_cu_hlg_hr.employee_school_level', string='Degree Level')

    _sql_constraints = [
        ('code', 'unique (code)', 'The code must be unique!')
    ]


class Degree(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.degree'

    name = fields.Char('Name', size=150, required=True)
    degree_level_id = fields.Many2one('l10n_cu_hlg_hr.employee_school_level', string='Degree Level',
                                      domain="[('code','in',[2020,2021,2023])]")
    code = fields.Char(required=True)
    branch_science_id = fields.Many2one('l10n_cu_hlg_hr_work_force.branch_science', string='Branch Science')
    specialty_family_id = fields.Many2one('l10n_cu_hlg_hr_work_force.specialty_family', string='Specialty Family')
    parent_code = fields.Char('Parent Code')
    parent_id = fields.Many2one('l10n_cu_hlg_hr_work_force.degree', string='Degree parent', ondelete='cascade', index=True)
    child_ids = fields.One2many('l10n_cu_hlg_hr_work_force.degree', 'parent_id', string='Childs Degrees')

    @api.onchange('degree_level_id')
    def _get_domain_especiality(self):
        for model in self:
            self.specialty_family_id = False

            if model.degree_level_id:
                return {'domain': {'specialty_family_id': [('degree_level_id', '=', model.degree_level_id.id)],
                                   'branch_science_id': [('degree_level_id', '=', model.degree_level_id.id)]}}

    _sql_constraints = [
        ('code', 'unique (code)', 'The code must be unique!')
    ]


############# models for use in GFORZA xmls directly ############################

# class Employed(models.Model):
#     _name = 'l10n_cu_hlg_hr_work_force.employed'
#
#     #code ministry + code entity + code degree + code municipality + code state + code age range + code contract type + year do
#     code = fields.Char(required=True)
#     entity_id = fields.Many2one('res.partner', string='Entity', required=True)
#     degree_id = fields.Many2one('l10n_cu_hlg_hr_work_force.degree', string='Degree', required=True)
#     municipality_id = fields.Many2one('l10n_cu_base.municipality', string='Municipality', required=True)
#     contract_type_id = fields.Many2one('l10n_cu_hlg_hr_work_force.contract_type', string='Employment', required=True)
#     age_range_id = fields.Many2one('l10n_cu_hlg_hr_work_force.age_range', string='Age Range', required=True)
#     count_graduates = fields.Integer(string='Count of graduates', required=True)
#     year_do = fields.Integer(string = 'Year do', required=True)
#
#     _sql_constraints = [
#         ('code', 'unique (code)', 'The code must be unique!')


class AgeRange(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.age_range'
    _description = 'Age range for Gforza Export'

    code = fields.Char(required=True)
    name = fields.Char('Name', size=150, required=True)

    _sql_constraints = [
        ('code', 'unique (code)', 'The code must be unique!')
    ]


class ContractType(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.contract_type'
    _description = 'Contract Type for Gforza Export'

    code = fields.Char(required=True)
    name = fields.Char('Name', size=150, required=True)

    _sql_constraints = [
        ('code', 'unique (code)', 'The code must be unique!')
    ]


class Employment(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.employment'
    _description = 'Employment for Gforza Export'

    code = fields.Char(required=True)
    name = name = fields.Char('Name', size=150, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    _sql_constraints = [
        ('code', 'unique (code)', 'The code must be unique!')
    ]


class HireDropRecord(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.hire_drop_record'
    _description = 'Hire and Drop Record'

    name = fields.Char(string='Name')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    motive_id = fields.Many2one('hr_contract.supplement_motive', string='Motive', required=True)
    record_date = fields.Date(string='Record date', required=True)
    record_type = fields.Selection([('hire', 'Hire'), ('drop', 'Drop')], string='Type')
    company_id = fields.Many2one('res.company', string='Entity', default=lambda self: self.env.user.company_id)


class GraduatesDemand(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.graduates_demand'
    _description = 'Graduates Demand'

    def _get_domain_state(self):
        return "[('country_id', '=', " + str(self.env.ref('base.cu').id) + ")]"

    def _get_domain_period(self):
        current_year = datetime.today().year
        years = [str(current_year), str(current_year + 1)]
        return "[('annual', '=', True), ('name', 'in', " + str(years) + ")]"

    code_ftc3 = fields.Char(string='Code for FTC3')
    code_ftc4 = fields.Char(string='Code for FTC4')
    ministry_id = fields.Many2one('l10n_cu.ministry', string='Ministry', required=True)
    organism_id = fields.Many2one('l10n_cu_hlg_hr_work_force.organism', string='Organism', required=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True, domain=_get_domain_state)
    municipality_id = fields.Many2one('l10n_cu_base.municipality', string='Municipality', required=True)
    entity_id = fields.Many2one('res.company', string='Entity', required=True, default=lambda self: self.env.user.company_id)
    degree_id = fields.Many2one('l10n_cu_hlg_hr_work_force.degree', string='Degree', required=True)
    line_ids = fields.One2many('l10n_cu_hlg_hr_work_force.graduates_demand_line', 'demand_id', string='Demand')
    period_id = fields.Many2one('l10n_cu_period.period', string='Fiscal year', required=True, domain=_get_domain_period)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = _("Demand") + " %s / %s / %s" % (record.degree_id.name, record.entity_id.name, record.period_id.name)
            result.append((record.id, name))
        return result

    @api.model
    def create_new_period(self):
        period_obj = self.env['l10n_cu_period.period']
        last_period = period_obj.search([('annual', '=', True)], order='name DESC', limit=1)
        date_start = (datetime.strptime(last_period.date_start, '%Y-%m-%d') + relativedelta(years=+1)).strftime('%Y-%m-%d')
        date_stop = (datetime.strptime(last_period.date_stop, '%Y-%m-%d') + relativedelta(years=+1)).strftime('%Y-%m-%d')
        period_obj.create({'name': str(int(last_period.name) + 1), 'annual': True,
                           'date_start': date_start, 'date_stop': date_stop})

    @api.onchange('period_id')
    def _onchange_period(self):
        if self.period_id:
            self.line_ids = [(0, 0, {'period_id': p.id})
                             for p in self.env['l10n_cu_period.period'].search([('annual', '=', True),
                                                                                ('date_start', '>', self.period_id.date_start)],
                                                                               limit=10, order='name')]
        else:
            self.line_ids = None

    _sql_constraints = [
        ('unique_entity_year_degree', 'unique (entity_id, degree_id, period_id)',
         _('The demand must be unique per degree, entity and year!')),

        ('code_ftc3', 'unique (code_ftc3)', _('The code_ftc3 must be unique!')),

        ('code_ftc4', 'unique (code_ftc4)', _('The code_ftc4 must be unique!'))
    ]


class GraduatesDemandLine(models.Model):
    _name = 'l10n_cu_hlg_hr_work_force.graduates_demand_line'
    _description = 'Graduates Demand Line'

    demand_id = fields.Many2one('l10n_cu_hlg_hr_work_force.graduates_demand', string='Demand', ondelete='cascade', required=True)
    period_id = fields.Many2one('l10n_cu_period.period', string='Year', required=True, domain=[('annual', '=', True)])
    quantity = fields.Integer(string='Quantity', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

