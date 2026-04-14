# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, tools
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ReportWzd(models.TransientModel):
    _name = 'l10n_cu_hlg_hr_work_force.report_wzd'

    def get_parent_degree_domain(self):
        parents = []
        for d in self.env['l10n_cu_hlg_hr_work_force.degree'].search([]):
            if d.parent_id.id and d.parent_id.id not in parents:
                parents.append(d.parent_id.id)
        return "[('id', 'in', " + str(parents) + ")]"

    reports = fields.Selection([('degree', 'Degree'), ('employee', 'Employees'), ('hire_drop', 'Hired Drop'),
                                ('demand', 'Graduates demand')], string='Reports', default='degree')

    degree_filter = fields.Selection([('all', 'All'), ('branch', 'Branch Science'), ('specialty', 'Specialty Family'),
                                      ('parent', 'Degree Parent')], string='Filter by', default='all')
    demand_filter = fields.Selection([('year', 'Year'), ('degree', 'Degree')], string='Filter by', default='year')
    employee_filter = fields.Selection([('occupational', 'Occupational Category'), ('age_range', 'Age Range')],
                                       string='Filter by', default='occupational')
    hire_drop_filter = fields.Selection([('age_range', 'Age Range'), ('gender', 'Gender'), ('motive', 'Motive')],
                                        string='Filter by', default='age_range')

    branch_science_id = fields.Many2one('l10n_cu_hlg_hr_work_force.branch_science', string='Branch Science')
    specialty_family_id = fields.Many2one('l10n_cu_hlg_hr_work_force.specialty_family', string='Specialty Family')
    parent_id = fields.Many2one('l10n_cu_hlg_hr_work_force.degree', string='Parent', domain=get_parent_degree_domain)
    degree_id = fields.Many2one('l10n_cu_hlg_hr_work_force.degree', string='Degree')
    period_id = fields.Many2one('l10n_cu_period.period', string='Year', domain=[('annual', '=', True)])
    occupational_id = fields.Many2one('l10n_cu_hlg_hr.occupational_category', string='Occupational Category')
    age_range_employee_id = fields.Many2one('l10n_cu_hlg_hr_work_force.age_range', string='Age Range')
    age_range_hire_drop_id = fields.Many2one('l10n_cu_hlg_hr_work_force.age_range', string='Age Range')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    motive_id = fields.Many2one('hr_contract.supplement_motive', string='Motive')

    @api.multi
    def report_print(self):
        degree_obj = self.env['l10n_cu_hlg_hr_work_force.degree']
        employee_obj = self.env['hr.employee']
        datas = {}

        if self.reports == 'degree':
            list_degree = []
            if self.degree_filter == 'all':
                datas['report_type'] = _('Degree List')
                degrees = degree_obj.search([])
            elif self.degree_filter == 'branch' and self.branch_science_id:
                datas['report_type'] = _('Degree list by Science branch: ') + self.branch_science_id.name
                degrees = degree_obj.search([('branch_science_id', '=', self.branch_science_id.id)])
            elif self.degree_filter == 'specialty' and self.specialty_family_id:
                datas['report_type'] = _('Degree list by family of specialities : ') + self.specialty_family_id.name
                degrees = degree_obj.search([('specialty_family_id', '=', self.specialty_family_id.id)])
            else:
                datas['report_type'] = _('Degree list by parent degree: ') + self.parent_id.name
                degrees = degree_obj.search([('parent_id', '=', int(self.parent_id.id))])

            for degree in degrees:
                data_degree = {'code': degree.code, 'name': degree.name,
                               'level': degree.degree_level_id.name if degree.degree_level_id.id else '-'}
                list_degree.append(data_degree)

            datas['list_degree'] = list_degree
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_hlg_hr_work_force.print_by_wzd_degree_report',
                'datas': datas,
            }

        if self.reports == 'demand':
            if self.demand_filter == 'year':
                datas['report_type'] = _('Graduates demand of year: ') + self.period_id.name
                demands = self.env['l10n_cu_hlg_hr_work_force.graduates_demand'].search(
                    [('period_id', '=', self.period_id.id)]
                )
                if len(demands) == 0:
                    raise ValidationError(_('There is not graduates demand for this year!'))
                
                periods = []
                for dl in demands[0].line_ids:
                    periods.append({'name': dl.period_id.name})
                datas['periods'] = periods
                
                dict_demands = {}
                list_entities = []
                for d in demands:
                    if d.entity_id.name not in dict_demands:
                        list_entities.append(d.entity_id.name)
                        years = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] = dl.quantity
                            total += dl.quantity

                        dict_demands[d.entity_id.name] = {
                            d.degree_id.degree_level_id.name: {
                                'degrees': {
                                    d.degree_id.name: {
                                        'years': years,
                                        'total': total
                                    }
                                },
                                'years': years,
                                'total': total,
                                'list_degrees': [d.degree_id.name]
                            },
                            'years': years,
                            'total': total,
                            'list_levels': [d.degree_id.degree_level_id.name]
                        }
                    elif d.degree_id.degree_level_id.name not in dict_demands[d.entity_id.name]:
                        years = dict_demands[d.entity_id.name]['years']
                        years_level = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] += dl.quantity
                            years_level[dl.period_id.name] = dl.quantity
                            total += dl.quantity

                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name] = {
                            'degrees': {
                                d.degree_id.name: {
                                    'years': years_level,
                                    'total': total
                                }
                            },
                            'years': years_level,
                            'total': total,
                            'list_degrees': [d.degree_id.name]
                        }
                        dict_demands[d.entity_id.name]['list_levels'].append(d.degree_id.degree_level_id.name)
                        dict_demands[d.entity_id.name]['years'] = years
                        dict_demands[d.entity_id.name]['total'] += total
                    elif d.degree_id.name not in dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['degrees']:
                        years = dict_demands[d.entity_id.name]['years']
                        years_level = dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['years']
                        years_degree = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] += dl.quantity
                            years_level[dl.period_id.name] += dl.quantity
                            years_degree[dl.period_id.name] = dl.quantity
                            total += dl.quantity

                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['degrees'][d.degree_id.name] = {
                            'years': years_degree,
                            'total': total
                        }
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['list_degrees'].append(d.degree_id.name)
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['years'] = years_level
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['total'] += total
                        dict_demands[d.entity_id.name]['years'] = years
                        dict_demands[d.entity_id.name]['total'] += total

                datas['list_entities'] = list_entities
                datas['dict_demands'] = dict_demands

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_hr_work_force.print_demand_year_report',
                    'datas': datas,
                }
            if self.demand_filter == 'degree':
                datas['report_type'] = _('Graduates demand of degree: ') + self.degree_id.name
                demands = self.env['l10n_cu_hlg_hr_work_force.graduates_demand'].search(
                    [('degree_id', '=', self.degree_id.id)]
                )
                if len(demands) == 0:
                    raise ValidationError(_('There is not graduates demand for this degree!'))

                periods = []
                list_periods = []
                for d in demands:
                    for dl in d.line_ids:
                        if dl.period_id.id not in list_periods:
                            list_periods.append(dl.period_id.id)
                            periods.append({'name': dl.period_id.name})
                datas['periods'] = periods

                dict_demands = {}
                list_entities = []
                for d in demands:
                    if d.entity_id.name not in dict_demands:
                        list_entities.append(d.entity_id.name)
                        years = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] = dl.quantity
                            total += dl.quantity
                        for p in periods:
                            if p['name'] not in years:
                                years[p['name']] = 0

                        dict_demands[d.entity_id.name] = {
                            d.degree_id.degree_level_id.name: {
                                'periods': {
                                    d.period_id.name: {
                                        'years': years,
                                        'total': total
                                    }
                                },
                                'years': years,
                                'total': total,
                                'list_periods': [d.period_id.name]
                            },
                            'years': years,
                            'total': total,
                            'list_levels': [d.degree_id.degree_level_id.name]
                        }
                    elif d.degree_id.degree_level_id.name not in dict_demands[d.entity_id.name]:
                        years = dict_demands[d.entity_id.name]['years']
                        years_level = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] += dl.quantity
                            years_level[dl.period_id.name] = dl.quantity
                            total += dl.quantity
                        for p in periods:
                            if p['name'] not in years_level:
                                years_level[p['name']] = 0

                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name] = {
                            'periods': {
                                d.period_id.name: {
                                    'years': years_level,
                                    'total': total
                                }
                            },
                            'years': years_level,
                            'total': total,
                            'list_degrees': [d.period_id.name]
                        }
                        dict_demands[d.entity_id.name]['list_levels'].append(d.degree_id.degree_level_id.name)
                        dict_demands[d.entity_id.name]['years'] = years
                        dict_demands[d.entity_id.name]['total'] += total
                    elif d.period_id.name not in dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['periods']:
                        years = dict_demands[d.entity_id.name]['years']
                        years_level = dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['years']
                        years_degree = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] += dl.quantity
                            years_level[dl.period_id.name] += dl.quantity
                            years_degree[dl.period_id.name] = dl.quantity
                            total += dl.quantity
                        for p in periods:
                            if p['name'] not in years_degree:
                                years_degree[p['name']] = 0

                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['periods'][d.period_id.name] = {
                            'years': years_degree,
                            'total': total
                        }
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['list_periods'].append(d.period_id.name)
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['years'] = years_level
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['total'] += total
                        dict_demands[d.entity_id.name]['years'] = years
                        dict_demands[d.entity_id.name]['total'] += total

                datas['list_entities'] = list_entities
                datas['dict_demands'] = dict_demands

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_hr_work_force.print_demand_degree_report',
                    'datas': datas,
                }

        if self.reports == 'employee':
            list_employee = []
            if self.employee_filter == 'occupational':
                employees = employee_obj.search([('occupational_category_id', '=', int(self.occupational_id.id))])
                dict_categories = {
                    'C': _('Directive'),
                    'A': _('Administrative'),
                    'T': _('Technician'),
                    'S': _('Service'),
                    'O': _('Workman'),
                    'E': _('Student')
                }
                if self.occupational_id.name in dict_categories:
                    category = dict_categories[self.occupational_id.name]
                else:
                    category = self.occupational_id.name
                datas['report'] = _('List of employees that has the %s category') % category

                for employee in employees:
                    data_employee = {'identification_id': employee.identification_id, 'name': employee.name,
                                     'degree': employee.degree_id.name if employee.degree_id.id else '-'}
                    list_employee.append(data_employee)

                datas['list_employee'] = list_employee

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_hr_work_force.employee_report',
                    'datas': datas,
                }
            elif self.employee_filter == 'age_range':
                employees = employee_obj.search([('age_range_id', '=', self.age_range_employee_id.id)])
                datas['report'] = _('List of employees in the %s age range') % self.age_range_employee_id.name

                for employee in employees:
                    data_employee = {'identification_id': employee.identification_id, 'name': employee.name,
                                     'degree': employee.degree_id.name if employee.degree_id.id else '-'}
                    list_employee.append(data_employee)

                datas['list_employee'] = list_employee

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_hr_work_force.employee_report',
                    'datas': datas,
                }

        if self.reports == 'hire_drop':
            hire_drop_obj = self.env['l10n_cu_hlg_hr_work_force.hire_drop_record']
            list_hire_drop = []
            if self.hire_drop_filter == 'age_range':
                datas['report'] = _('Employee hire and drop by %s age range') % self.age_range_hire_drop_id.name

                for hd in hire_drop_obj.search([]):
                    if hd.employee_id.age_range_id.id == self.age_range_hire_drop_id.id:
                        hire_drop_data = {
                            'employee': hd.employee_id.name,
                            'ci': hd.employee_id.identification_id,
                            'date': datetime.strptime(hd.record_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                            'type': dict(self.env['l10n_cu_hlg_hr_work_force.hire_drop_record'].fields_get(allfields=['record_type'])['record_type']['selection'])[hd.record_type],
                            'department': hd.employee_id.department_id.name if hd.employee_id.department_id.id else '-',
                            'motive': hd.motive_id.name
                        }
                        list_hire_drop.append(hire_drop_data)

            if self.hire_drop_filter == 'gender':
                datas['report'] = _('Employee hire and drop by %s gender') % self.gender

                for hd in hire_drop_obj.search([]):
                    if hd.employee_id.gender == self.gender:
                        hire_drop_data = {
                            'employee': hd.employee_id.name,
                            'ci': hd.employee_id.identification_id,
                            'date': datetime.strptime(hd.record_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                            'type': dict(self.env['l10n_cu_hlg_hr_work_force.hire_drop_record'].fields_get(allfields=['record_type'])['record_type']['selection'])[hd.record_type],
                            'department': hd.employee_id.department_id.name if hd.employee_id.department_id.id else '-',
                            'motive': hd.motive_id.name
                        }
                        list_hire_drop.append(hire_drop_data)

            if self.hire_drop_filter == 'motive':
                datas['report'] = _('Employee hire and drop by %s motive') % self.motive_id.name

                for hd in hire_drop_obj.search([('motive_id', '=', self.motive_id.id)]):
                    hire_drop_data = {
                        'employee': hd.employee_id.name,
                        'ci': hd.employee_id.identification_id,
                        'date': datetime.strptime(hd.record_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                        'type': dict(self.env['l10n_cu_hlg_hr_work_force.hire_drop_record'].fields_get(allfields=['record_type'])['record_type']['selection'])[hd.record_type],
                        'department': hd.employee_id.department_id.name if hd.employee_id.department_id.id else '-',
                        'motive': hd.motive_id.name
                    }
                    list_hire_drop.append(hire_drop_data)

            datas['list_hire_drop'] = list_hire_drop
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_hlg_hr_work_force.hire_drop_report',
                'datas': datas,
            }
