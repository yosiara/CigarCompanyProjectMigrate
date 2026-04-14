# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError
month_dic = {'01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril', '05': 'mayo', '06': 'junio',
             '07': 'julio', '08': 'agosto', '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'}


class RetiredPersonWizard(models.TransientModel):
    _name = 'turei_retired_person.wzd_retired_person_reports'

    @staticmethod
    def get_month_name(month):
        if month == '01':
            return 'january'
        elif month == '02':
            return 'february'
        elif month == '03':
            return 'march'
        elif month == '04':
            return 'april'
        elif month == '05':
            return 'may'
        elif month == '06':
            return 'june'
        elif month == '07':
            return 'july'
        elif month == '08':
            return 'august'
        elif month == '09':
            return 'september'
        elif month == '10':
            return 'october'
        elif month == '11':
            return 'november'
        elif month == '12':
            return 'december'


    reports = fields.Selection([('retired', 'Retired Person'), ('article', 'Article'),('employee','Employee Arrival Retired'),('dead','Dead Person')], string='Reports', default='retired')
    retired_person_filter = fields.Selection([('all', 'All Retired Person'), ('retired_year', 'Retired Year'),
                                              ('birth_month', 'Birht Month'),
                                              ('gender','Gender'),('ueb','UEB'),('job','Job'),('degree','Degree')],
                                       string='Filter by', default='all')
    retired_article_filter = fields.Selection([ ('year', 'Year'),
                                              ('article', 'Article'),
                                                ('article_type', 'Article Type')],
                                             string='Filter by', default='year')

    employee_filter = fields.Selection([ ('year', 'Year'),
                                              ('period', 'Period')],
                                             string='Filter by', default='year')

    dead_filter = fields.Selection([ ('year', 'Year'),
                                              ('period', 'Period')],
                                             string='Filter by', default='year')

    def get_retired_year(self):
        today = fields.Date.today()
        retired_year = today.split('-')
        retired_year = int(retired_year[0])

        retired_year_list = []
        for i in range(2004, retired_year + 1):
            retired_year_reg = (i, i)
            retired_year_list.append(retired_year_reg)
        return retired_year_list

    def get_arrival_year(self):
        today = fields.Date.today()
        retired_year = today.split('-')
        retired_year = int(retired_year[0])

        retired_year_list = []
        for i in range(retired_year, retired_year + 50):
            retired_year_reg = (i, i)
            retired_year_list.append(retired_year_reg)
        return retired_year_list

    retired_year = fields.Selection(selection='get_retired_year', String='Retired Year')
    retired_gender = fields.Selection([('Female', 'Female'), ('Male', 'Male')],
                                      string='Gender', default='Female')
    ueb_id = fields.Many2one('app_seleccion.area', string='UEB')
    job_id = fields.Many2one('hr.job', string='Job')
    degree_id = fields.Many2one('l10n_cu_hlg_uforce.degree', string='Degree')
    year = fields.Selection(selection='get_retired_year', string='Year')
    article_id = fields.Many2one('turei_retired_person.article_to_retired',string='Article')
    article_type_id = fields.Many2one('turei_retired_person.article_to_retired_type',string='Article Type')



    def get_month(self):
        month = []
        month.append(('01','january'))
        month.append(('02','february'))
        month.append(('03','march'))
        month.append(('04','april'))
        month.append(('05','may'))
        month.append(('06','june'))
        month.append(('07','july'))
        month.append(('08','august'))
        month.append(('09','september'))
        month.append(('10','october'))
        month.append(('11','november'))
        month.append(('12','december'))
        return month

    birth_month = fields.Selection(selection='get_month', String='Month')
    arrival_year = fields.Selection(selection='get_arrival_year', string='Arrival Year')
    start_year = fields.Selection(selection='get_arrival_year', string='Start Year')
    end_year = fields.Selection(selection='get_arrival_year', string='End Year')

    dead_year = fields.Selection(selection='get_retired_year', string='Year')
    start_dead_year = fields.Selection(selection='get_retired_year', string='Start Year')
    end_dead_year = fields.Selection(selection='get_retired_year', string='End Year')


    @api.multi
    def print_retired_person_reports(self):

        retired_person_obj = self.env['turei_retired_person.retired_person']
        retired_article_request_obj = self.env['turei_retired_person.article_request']
        employee_obj = self.env['hr.employee']
        datas = {}
        retired_list = []

        if self.reports == 'retired':
            if self.retired_person_filter == 'all':
                datas['report_type'] = _('Retired Person List All')
                retired_person = retired_person_obj.search([])
            elif self.retired_person_filter == 'retired_year':
                datas['report_type'] = _('Retired Person in: '+self.retired_year)
                retired_person = retired_person_obj.search([('retired_year','=',int(self.retired_year))])
            elif self.retired_person_filter == 'gender':
                datas['report_type'] = _('Retired Person by gender: '+self.retired_gender)
                retired_person = retired_person_obj.search([('gender','=',self.retired_gender)])
            elif self.retired_person_filter == 'ueb':
                datas['report_type'] = _('Retired Person by UEB: '+self.ueb_id.name)
                retired_person = retired_person_obj.search([('ueb_id','=',self.ueb_id.id)])
            elif self.retired_person_filter == 'job':
                datas['report_type'] = _('Retired Person by Job: '+self.job_id.name)
                retired_person = retired_person_obj.search([('job_id','=',self.job_id.id)])
            elif self.retired_person_filter == 'degree':
                datas['report_type'] = _('Retired Person by Degree: '+self.degree_id.name)
                retired_person = retired_person_obj.search([('degree_id','=',self.degree_id.id)])
            elif self.retired_person_filter == 'birth_month':
                datas['report_type'] = _('Retired Person by Birth Month: '+self.get_month_name(self.birth_month))
                retired_person = retired_person_obj.search([('birth_month','=',self.birth_month)])



            for retired in retired_person:
                data_retired = {'identification_id': retired.identification_id if retired.identification_id else '-', 'name': retired.name,
                                'address': retired.address if retired.address else '-', 'neighborhood': retired.neighborhood_id.name if retired.neighborhood_id.name else '-',
                                'municipality': retired.municipality_id.name, 'state': retired.state_id.name,
                                'retired_date': retired.retired_date}
                retired_list.append(data_retired)

            datas['retired_list'] = retired_list


            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'turei_retired_person.report_retired_person',
                'datas': datas,
            }
        elif self.reports == 'article':
            if self.retired_article_filter == 'year':
                datas['report_type'] = _('Request Article in: ' + self.year)
                retired_article_request = retired_article_request_obj.search([('request_year', '=', self.year)])
            elif self.retired_article_filter == 'article':
                datas['report_type'] = _('Request Article is: ' + self.article_id.name)
                retired_article_request = retired_article_request_obj.search([('article_id', '=', self.article_id.id)])
            elif self.retired_article_filter == 'article_type':
                datas['report_type'] = _('Request Article Type is: ' + self.article_type_id.name)
                retired_article_request = retired_article_request_obj.search([('article_id.article_to_retired_type_id','=',self.article_type_id.id)])


            for retired in retired_article_request:
                data_retired = {'identification_id': retired.retired_person_id.identification_id if self.retired.retired_person_id.identification_id else '-', 'name': retired.retired_person_id.name,
                                'article': retired.article_id.name, 'article_type': retired.article_id.article_to_retired_type_id.name,
                                'date': retired.date_request}
                retired_list.append(data_retired)

            datas['retired_list'] = retired_list

            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'turei_retired_person.report_retired_article_request',
                'datas': datas,
            }
        elif self.reports == 'employee':
            if self.employee_filter == 'year':
                datas['report_type'] = _('Employee arrival retired in: ' + self.arrival_year)
                employee = employee_obj.search([('retired_year','=',int(self.arrival_year))])

                for retired in employee:
                    data_retired = {'identification_id': retired.identification_id if self.retired.retired_person_id.identification_id else '-',
                                            'name': retired.name_related,
                                            'ueb': retired.department_id.name if retired.department_id.id else '-',
                                            'job': retired.job_id.name if retired.job_id.id else '-',
                                            'degree': retired.degree_id.name if retired.degree_id.id else '-'
                                            }
                    retired_list.append(data_retired)

                datas['retired_list'] = retired_list

                return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'turei_retired_person.report_employee_arrival_retired',
                        'datas': datas,
                    }
            else:

                datas['report_type'] = _('Employee arrival retired in period: ' + self.start_year+'-'+self.end_year)
                employee = employee_obj.search([('retired_year', '>=', int(self.start_year)),('retired_year', '<=', int(self.end_year))])

                for retired in employee:
                    data_retired = {'identification_id': retired.identification_id if self.retired.retired_person_id.identification_id else '-',
                                    'name': retired.name_related,
                                    'ueb': retired.department_id.name if retired.department_id.id else '-',
                                    'job': retired.job_id.name if retired.job_id.id else '-',
                                    'degree': retired.degree_id.name if retired.degree_id.id else '-'
                                    }
                    retired_list.append(data_retired)

                datas['retired_list'] = retired_list

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'turei_retired_person.report_employee_arrival_retired',
                    'datas': datas,
                }
        elif self.reports == 'dead':
            if self.dead_filter == 'year':
                datas['report_type'] = _('Retired Person Dead in: ' + self.dead_year)
                retired_person = retired_person_obj.search([('dead_year','=',int(self.dead_year))])

                for retired in retired_person:
                    data_retired = {'identification_id': retired.identification_id if self.retired.retired_person_id.identification_id else '-',
                                            'name': retired.name,
                                            'address': retired.address if retired.address else '-',
                                            'retired_date': retired.retired_date,
                                            'dead_date': retired.dead_date if retired.dead_date else '-'
                                            }
                    retired_list.append(data_retired)

                datas['retired_list'] = retired_list

                return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'turei_retired_person.report_dead_person',
                        'datas': datas,
                    }
            else:
                datas['report_type'] = _('Retired Person Dead in period: ' + self.start_dead_year + '-'+ self.end_dead_year )
                retired_person = retired_person_obj.search([('dead_year', '>=', int(self.start_dead_year)),('dead_year', '<=', int(self.end_dead_year))])

                for retired in retired_person:
                    data_retired = {'identification_id': retired.identification_id if self.retired.identification_id else '-',
                                    'name': retired.name,
                                    'address': retired.address if retired.address else '-',
                                    'retired_date': retired.retired_date,
                                    'dead_date': retired.dead_date if retired.dead_date else '-'
                                    }
                    retired_list.append(data_retired)

                datas['retired_list'] = retired_list

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'turei_retired_person.report_dead_person',
                    'datas': datas,
                }


    @api.constrains('start_year','end_year')
    def _check_period(self):
        if self.start_year > self.end_year:
            raise ValidationError(_("The start year must be less than the end year !!"))

    @api.constrains('start_dead_year', 'end_dead_year')
    def _check_period_dead(self):
        if self.start_dead_year > self.end_dead_year:
            raise ValidationError(_("The start year must be less than the end year !!"))
