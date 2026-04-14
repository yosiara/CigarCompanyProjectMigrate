# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, tools, _
from datetime import timedelta, datetime, date


class RetiredPerson(models.Model):
    _name = 'turei_retired_person.retired_person'


    @api.model
    def _get_default_municipality(self):
        return self.env['l10n_cu_base.municipality'].search([('name', '=', 'Holguín')], limit=1).id

    @api.model
    def _get_default_state(self):
        return self.env['res.country.state'].search([('name', '=', 'Holguín')], limit=1).id

    identification_id = fields.Char(string='Identification ID', size=11)
    #in case not identification_id
    born_date = fields.Date('Born Date')
    name = fields.Char('Name', size=60, required=True)
    address = fields.Char('Address', size=120)
    neighborhood_id = fields.Many2one('app_seleccion.reparto',string='Neighborhood')
    municipality_id = fields.Many2one('l10n_cu_base.municipality', string='Municipality',
                                      default=_get_default_municipality)
    state_id = fields.Many2one('res.country.state', string='State', ondelete='restrict',
                               default=_get_default_state)
    dead_person = fields.Boolean('Is dead retired person?')
    dead_person_description = fields.Char('Dead Person Description', compute='_set_dead_person_description', store=True)
    dead_date = fields.Date('Dead Date')
    dead_year = fields.Integer('Dead Year', compute='_set_dead_year', store=True)

    @api.depends('dead_date')
    def _set_dead_year(self):
        if self.dead_date:
            dead_d = self.dead_date
            dead_y = dead_d.split('-')
            dead_y = dead_y[0]
            self.dead_year = int(dead_y)

    @api.depends('dead_person')
    def _set_dead_person_description(self):
        if self.dead_person == True:
            self.dead_person_description = 'Fallecido'
        else:
            self.dead_person_description = 'No fallecido'




    retired_date = fields.Date('Retired Date', required=True)
    retired_year = fields.Integer('Retired Year', compute='_set_retired_year', store=True)

    @api.depends('retired_date')
    def _set_retired_year(self):
        if self.retired_date:
            retired_d = self.retired_date
            retired_y = retired_d.split('-')
            retired_y = retired_y[0]
            self.retired_year = int(retired_y)



    ueb_id = fields.Many2one('app_seleccion.area', string='UEB', ondelete='set null')

    founder = fields.Boolean('Founder?')
    founder_description = fields.Char('Founder Description', compute='_set_founder_description', store=True)

    @api.depends('founder')
    def _set_founder_description(self):
        if self.founder == True:
            self.founder_description = 'Fundador'
        else:
            self.founder_description = 'No Fundador'

    retired_job_id = fields.Many2one('hr.job','Retired Job')
    degree_id = fields.Many2one('l10n_cu_hlg_uforce.degree', string='Degree')
    in_service = fields.Boolean('In Service?')
    house_phone = fields.Char('House Phone', Size='60')
    cell_phone = fields.Char('Cell Phone', Size='60')
    email = fields.Char('Email', Size='100')

    article_request_id = fields.One2many(comodel_name='turei_retired_person.article_request',inverse_name='retired_person_id',string='Article Request')
    gender_choice = fields.Selection([('female', 'Female'),('male', 'Male')],
                                             string='Gender')
    gender = fields.Char(string='Gender', store=True, compute='_compute_gender')

    @api.depends('identification_id','gender_choice')
    def _compute_gender(self):
        if self.identification_id != False:
            if len(self.identification_id) == 11:
                if int(self.identification_id[9]) % 2 == 0:
                    self.gender = 'Male'
                else:
                    self.gender = 'Female'
        if self.gender_choice == 'female':
            self.gender = 'Female'
        else:
            self.gender = 'Male'

    @api.onchange('identification_id')
    def _complete_gender(self):
        if self.identification_id:
            if len(self.identification_id) == 11:
                if int(self.identification_id[9]) % 2 == 0:
                    self.gender = 'Male'
                    self.gender_choice = 'male'
                else:
                    self.gender = 'Female'
                    self.gender_choice = 'female'


    birth_month = fields.Char(string='Birth Month', store=True, compute='_compute_birth_month')
    birth_month_name = fields.Char(string='Birth Month', store=True, compute='_compute_birth_month')

    @api.depends('identification_id','born_date')
    def _compute_birth_month(self):
        if self.identification_id != False:
            if len(self.identification_id) == 11:
                self.birth_month = self.identification_id[2:4]
        elif self.born_date:
            born_d = self.born_date
            born_m = born_d.split('-')
            born_m = born_m[1]
            self.birth_month = born_m

        if self.birth_month == '01':
            self.birth_month_name = 'january'
        elif self.birth_month == '02':
            self.birth_month_name = 'february'
        elif self.birth_month == '03':
            self.birth_month_name = 'march'
        elif self.birth_month == '04':
            self.birth_month_name = 'april'
        elif self.birth_month == '05':
            self.birth_month_name = 'may'
        elif self.birth_month == '06':
            self.birth_month_name = 'june'
        elif self.birth_month == '07':
            self.birth_month_name = 'july'
        elif self.birth_month == '08':
            self.birth_month_name = 'august'
        elif self.birth_month == '09':
            self.birth_month_name = 'september'
        elif self.birth_month == '10':
            self.birth_month_name = 'october'
        elif self.birth_month == '11':
            self.birth_month_name = 'november'
        elif self.birth_month == '12':
            self.birth_month_name = 'december'

    # @api.constrains('identification_id', 'born_date')
    # def _check_born_data(self):
    #     if not self.identification_id and not self.born_date:
    #         raise ValidationError(_("Is necesary Identification ID or Born Date !!"))
    #
    # @api.constrains('identification_id', 'gender_choice')
    # def _check_gender_data(self):
    #     if not self.identification_id and not self.gender_choice:
    #         raise ValidationError(_("Is necesary Identification ID or Gender Choice !!"))


class ArticleRequest(models.Model):
    _name = 'turei_retired_person.article_request'

    retired_person_id = fields.Many2one('turei_retired_person.retired_person', string='Retired Person', required=True, ondelete='cascade')
    article_id = fields.Many2one('turei_retired_person.article_to_retired',string='Article', required=True)
    article_type = fields.Char(related='article_id.article_to_retired_type_id.name',string='Article Type',store=True)
    date_request = fields.Date('Date Request',required=True)
    request_year = fields.Integer('Request Year', compute='_set_request_year', store=True)

    @api.depends('date_request')
    def _set_request_year(self):
        if self.date_request:
            request_d = self.date_request
            request_y = request_d.split('-')
            request_y = request_y[0]
            self.request_year = int(request_y)

    assigned = fields.Boolean('Assigned')



# to determinate the year of retired for employees
class Employee(models.Model):
    _inherit = 'hr.employee'

    retired_year = fields.Integer(string='Retired Year',compute='_compute_retired_year',store=True)

    @api.depends('identification_id')
    def _compute_retired_year(self):
        if self.identification_id and len(self.identification_id) == 11:
            today_date = fields.Date.today()
            array_date = today_date.split('-')
            arr = array_date[0]
            year_actualr = arr[2:]
            year_employee = self.identification_id[0:2]

            if int(year_employee) > int(year_actualr):
                year_employee = 1900 + int(year_employee)
            else:
                year_employee = 2000 + int(year_employee)

            if self.gender == 'Male':
                self.retired_year = year_employee + 65
            else:
                self.retired_year = year_employee + 60