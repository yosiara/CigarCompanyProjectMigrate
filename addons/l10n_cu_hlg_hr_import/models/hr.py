# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Position(models.Model):
    _inherit = "l10n_cu_hlg_hr.position"
    external_id = fields.Char('External Id')


class Department(models.Model):
    _inherit = "hr.department"
    external_id = fields.Char('External Id')
    # external_area_id = fields.Char('External area Id')


class Job(models.Model):
    _inherit = "hr.job"
    external_id = fields.Char('External Id')

    _sql_constraints = [
        # ('name_company_uniq', 'Check(1=1)', 'The name of the job position must be unique per department in company!'),
        ('name_company_uniq', 'unique(name, company_id, department_id,external_id)',
         'The name of the job position must be unique per department in company!'),
    ]


class Employee(models.Model):
    _inherit = "hr.employee"
    external_id = fields.Char('External Id')

    @api.multi
    def write(self, vals):
        if 'code' in vals:
            vals['external_id'] = vals['code']
        return super(Employee, self).write(vals)

    @api.model
    def create(self, vals):
        if 'code' in vals:
            vals['external_id'] = vals['code']
        return super(Employee, self).create(vals)


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"
    external_id = fields.Char('External Id')


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"
    external_id = fields.Char('External Id')
