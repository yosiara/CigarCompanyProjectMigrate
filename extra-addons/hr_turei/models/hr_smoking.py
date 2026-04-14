# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


# -*- coding: utf-8 -*-
import pytz
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class DailySmoking(models.Model):
    _name = 'hr_turei.daily_smoking'
    _rec_name = 'area'

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get()
        return company_id

    area = fields.Char('Area', compute='_compute_name', readonly=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    external_staff = fields.Boolean('External Staff', required=True, default=False)
    department_id = fields.Many2one('hr.department', string='Department')
    external_area_id = fields.Many2one('hr_turei.external_area', string='Area')
    pick_up = fields.Many2one('hr.employee', string='Pick up cigarettes')
    pick_up_sub = fields.Many2one('hr.employee', string='Pick up cigarettes(Substitute)')
    external_area_pick_up = fields.Many2one('hr_turei.external_staff', string='Pick up cigarettes')
    external_area_pick_up_sub = fields.Many2one('hr_turei.external_staff', string='Pick up cigarettes(Substitute)')

    def _compute_name(self):
        for record in self:
            record.area = record.department_id.name if record.department_id else record.external_area_id.name


class CigaretteConcept(models.Model):
    _name = 'hr_turei.cigarette_concept'

    name = fields.Char(string='Name', required=True)
    packs_amount = fields.Integer(string='Packs', required=True)
    delivery_frequency = fields.Selection([('per_day', 'Per Day'), ('per_hour', 'Per Hour'), ('per_week', 'Weekly'), ('per_month', 'Monthly')], string='Delivery Frequency', required=True, default=False)
    department_ids = fields.Many2many('hr.department', 'hr_turei_concept_departament_rel', 'concept_id', 'department_id',
                                      string='Departments')
    type = fields.Selection([('normal', 'Normal'), ('incentive', 'Incentive by accomplish'), ('to_insert', 'To Insert')], string='Type', required=True, default='normal')
    lower_limit = fields.Integer(string='Lower overcompliance percent limit')
    upper_limit = fields.Integer(string='Upper overcompliance percent limit')
    hours_perday = fields.Integer(string='Hours per labor journey', default=8)


class SmokePeriod(models.Model):
    _name = 'hr_turei.smoke_period'

    name = fields.Char(string='Identifier', required=True)
    start_date_production = fields.Date(string='Start Date Production', required=True)
    end_date_production = fields.Date(string='End Date Production', required=True)
    state = fields.Selection([('open', 'Open'), ('closed', 'Closed')], string='State', required=True)
    start_date = fields.Date(string='Start Date Labor Journeys', required=True)
    end_date = fields.Date(string='End Date Labor Journeys', required=True)
    include_monthly_areas = fields.Boolean('Include Monthly Areas', required=True, default=False)
    include_monthly_concepts = fields.Boolean('Include Monthly Concepts', required=True, default=False)
    resource_calendar_ids = fields.Many2many('resource.calendar', 'hr_turei_smoke_period_resource_calendar_rel', 'smoke_period_id', 'resource_calendar_id', 'Turns', required=True)

    @api.onchange('start_date', 'end_date')
    def _onchange_name(self):
        name = ''
        if self.start_date and self.end_date:
            start_date = self.invert_date(self.start_date)
            end_date = self.invert_date(self.end_date)
            name = _('Cigarette list from %s to %s.') % (start_date, end_date)
        self.name = name

    def invert_date(self, aux_date):
            return aux_date[8:10]+"/"+aux_date[5:7]+"/"+aux_date[0:4]


class AdditionalIncidencesLine(models.Model):
    _name = 'hr_turei.additional_incidences.line'

    concept_id = fields.Many2one('hr_turei.cigarette_concept', string='Concept', domain=[('type', '=', 'to_insert')])
    hours_amount = fields.Float(string='Hours Amount')
    packs = fields.Integer(string='Packs', required=True)
    cause = fields.Char(string='Cause')
    additional_incidences_id = fields.Many2one('hr_turei.additional_incidences', string='Additional Incidences')


class AdditionalIncidences(models.Model):
    _name = 'hr_turei.additional_incidences'

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get()
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)

    name = fields.Char('Name', readonly=True, compute='_compute_name')
    employee = fields.Boolean('Is an Employee', required=True, default=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    external_staff_id = fields.Many2one('hr_turei.external_staff', string='External Staff')
    code = fields.Char(string='Code', readonly=True)
    period_id = fields.Many2one('hr_turei.smoke_period', string='Period', domain=([('state', '=', 'open')]), required=True)
    line_ids = fields.One2many('hr_turei.additional_incidences.line', 'additional_incidences_id',
                                                       string='Incidences')

    def _compute_name(self):
        for record in self:
            if record.employee:
                record.name = record.employee_id.name
            else:
                record.name = record.external_staff_id.name

    @api.onchange('employee_id', 'external_staff_id')
    def _onchange_person(self):
        if self.employee:
            self.code = self.employee_id.code
        else:
            self.code = self.external_staff_id.code

    _sql_constraints = [
        ('employee_period_uniq', 'unique(employee_id, external_staff_id, period_id)', 'La persona que intenta añadir ya tiene un registro de incidencias adicionales en este periodo.'),
    ]
