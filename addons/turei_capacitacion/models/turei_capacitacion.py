# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, tools, _
from datetime import timedelta, datetime, date



class FormationMode(models.Model):
    _name = 'turei_capacitacion.formation_mode'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Exist one Formation Mode with this name !'),
    ]


class FormationCenter(models.Model):
    _name = 'turei_capacitacion.formation_center'

    name = fields.Char(string='Name', required=True)
    address = fields.Char(string='Address')
    description = fields.Text(string='Description')

    @api.model
    def _get_default_municipality(self):
        return self.env['l10n_cu_base.municipality'].search([('name', '=', 'Holguín')], limit=1).id

    @api.model
    def _get_default_state(self):
        return self.env['res.country.state'].search([('name', '=', 'Holguín')], limit=1).id

    municipality_id = fields.Many2one('l10n_cu_base.municipality', string='Municipality',
                                      default=_get_default_municipality)
    state_id = fields.Many2one('res.country.state', string='State', ondelete='restrict',
                               default=_get_default_state)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Exist one Formation Center with this name !'),
    ]

class InstructorCategorie(models.Model):
    _name = 'turei_capacitacion.instructor_categorie'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')


    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Exist one Instructor Categorie with this name !'),
    ]


class Instructor(models.Model):
    _name = 'turei_capacitacion.instructor'

    name = fields.Char(string='Name', required=True)
    ci = fields.Char(string='CI')
    street = fields.Char(string='Street')
    neighborhood_id = fields.Many2one('app_seleccion.reparto', string='Neighborhood')
    ueb_id = fields.Many2one('app_seleccion.ueb', string='UEB')
    job_id = fields.Many2one('hr.job', string="Applied Job")
    degree_id = fields.Many2one('l10n_cu_hlg_uforce.degree', string='Degree')
    phone = fields.Char(stroing='Phone')
    mobile_phone = fields.Char(string='Mobile Phone')
    email = fields.Char(string='Email')
    instructor_categorie_id = fields.Many2one('turei_capacitacion.instructor_categorie', string='Instructor Categorie')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Exist one Instructor with this name !'),
    ]


class CapacitationAction(models.Model):
    _name = 'turei_capacitacion.capacitation_action'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    capacitation_categorie_id = fields.Many2one('turei_capacitacion.capacitation_categorie', string='Capacitation Categorie ID')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    anual_period = fields.Many2one('l10n_cu_period.period', string='Anual Period', compute='_get_anual_period', store=True)
    estimate = fields.Float(string='Estimate')
    formation_mode_id = fields.Many2one('turei_capacitacion.formation_mode', string='Formation Mode')
    formation_center_id = fields.Many2one('turei_capacitacion.formation_center', string='Formation Center')
    quantity = fields.Integer(string='Quantity participants')
    department_participants_ids = fields.Many2many('hr.department', string='Groups Participants')
    individual_participants_ids = fields.Many2many('hr.employee',string='Individual Participants')

    @api.model
    @api.depends('start_date')
    def _get_anual_period(self):
        for rec in self:
            date_temp = str(rec.start_date).split('-')
            year = date_temp[0]

            rec_period_ids = self.env['l10n_cu_period.period'].search([('annual','=',True)])

            for rec_p in rec_period_ids:
                year_tmp = str(rec_p.date_start).split('-')
                year_tmp = year_tmp[0]

                if year_tmp == year:
                    rec.anual_period = rec_p.id
                    break




    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Exist one Capacitation Action with this name !'),
    ]

class IndividualPlanLines(models.Model):
    _name = 'turei_capacitacion.capacitation_ind_plan_lines'

    need_capacitation_id = fields.Many2one('turei_capacitacion.capacitation_need', string='Need Id')
    specific_theme = fields.Char(string='Specific Theme')
    formation_mode_id = fields.Many2one('turei_capacitacion.formation_mode', string='Formation Mode')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    external = fields.Boolean(string='External')
    internal = fields.Boolean(string='Internal')


class NeedPerCompetenceLines(models.Model):
    _name = 'turei_capacitacion.capacitation_need_competence_lines'

    need_capacitation_id = fields.Many2one('turei_capacitacion.capacitation_need', string='Need Id')
    know_how = fields.Char(string='Know-how')
    habilitie = fields.Char(string='Habilitie')

class NeedCapacitation(models.Model):
    _name = 'turei_capacitacion.capacitation_need'
    _rec_name = 'description'

    department_id = fields.Many2one('hr.department', string='Department', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, domain="[('department_id','=',department_id)]")
    school_level_id = fields.Many2one('l10n_cu_hlg_hr.employee_school_level', related="employee_id.school_level_id", string='School Level', store=True)
    occupational_category_id = fields.Many2one('l10n_cu_hlg_hr.occupational_category', related="employee_id.occupational_category_id",
                                               string='Occupational Category', store=True)
    attitudes = fields.Text(string='Attitudes')

    validation_date = fields.Many2one('l10n_cu_period.period', string='Validation Date', domain="[('annual','=', False)]", required=True)
    date_to = fields.Many2one('l10n_cu_period.period', string='Date To', domain="[('annual','=', False)]", required=True)
    need_per_compentence_line_ids = fields.One2many('turei_capacitacion.capacitation_need_competence_lines', 'need_capacitation_id', string='Need per competence'  )
    capacitation_plan_ind_lines_ids = fields.One2many('turei_capacitacion.capacitation_ind_plan_lines', 'need_capacitation_id', string='Individual Plan Line'  )
    description = fields.Char(string='Description', compute='_get_description')


    @api.depends('employee_id')
    def _get_description(self):
        for rec in self:
            if rec.employee_id:
                rec.description = _('Need Capacitation for: ') + rec.employee_id.name


    annual_period = fields.Many2one('l10n_cu_period.period', string='Annual Period', compute="_get_anual_period", store=True)

    @api.depends('validation_date')
    def _get_anual_period(self):
        for rec in self:
            date_tmp = rec.validation_date.date_start
            annual_perio_id = self.env['l10n_cu_period.period'].search([('date_start','<=', date_tmp),('date_stop','>=',date_tmp),('annual','=',True)],limit=1)
            rec.annual_period = annual_perio_id

