# -*- coding: utf-8 -*-

# import datetime
import re
from email.utils import formataddr
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.translate import _
from datetime import datetime, timedelta
import calendar

class ResourceResource(models.Model):
    _inherit = "resource.resource"

    _sql_constraints = [
        ('code_company_uniq', 'unique (code, company_id)', 'The code of the employee must be unique per company !'),
    ]


class Employee(models.Model):
    _inherit = "hr.employee"

    school_level_id = fields.Many2one('l10n_cu_hlg_hr.employee_school_level', string='School Level')
    age = fields.Integer('Age', readonly=True, compute='_compute_age', store=True)
    place_of_birth = fields.Char(string='Place of Birth')
    identification_id = fields.Char(string='Identification No', size=11)

    bank_secondary_account_id = fields.Many2one(
        'res.partner.bank', help='This account is used to secundary currency payment'
    )

    race = fields.Selection(
        [('black', 'Black'), ('white', 'White'), ('mixed', 'Mixed')],
        string='Skin color', translate=True
    )

    political_affiliation = fields.Selection(
        [('pcc', 'PCC'), ('ujc', 'UJC'), ('both', 'Doble Militancia'), ('none', _('None'))],
        string='Political Affiliation', translate=True
    )

    occupational_category_id = fields.Many2one(
        related='job_id.position_id.salary_group_id.occupational_category_id', string='Occupational Category',
        store=True, readonly=True
    )

    # Employment Information...
    admission_date = fields.Date('Admission Date')
    init_work_date = fields.Date('Init Work Date')
    date_organism = fields.Date('Admission date in organism')
    years_worked = fields.Integer(compute='_compute_years_worked', store=True)

    # Defence location...
    defence_location_id = fields.Many2one('l10n_cu_hlg_hr.employee_defence_location_type', string='Defence Location')
    date_defence_location_update = fields.Date(string='Updated')
    defence_situation = fields.Char(string='Situation')

    is_indispensable_employee = fields.Boolean(
        string='Is Indispensable Employee?', help='Selected if the employee is indispensable in his company...'
    )

    # @api.constrains('parent_id')
    # def _check_parent_id(self):
    #     for employee in self:
    #         if not employee.manager:
    #             if not employee._check_recursion():
    #                 raise ValidationError(_('Error! You cannot create recursive hierarchy of Employee(s).'))

    @api.one
    @api.depends('birthday')
    def _compute_age(self):
        if self.birthday:
            dBday = datetime.strptime(self.birthday, DEFAULT_SERVER_DATE_FORMAT).date()
            dToday = datetime.now().date()
            self.age = dToday.year - dBday.year - ((dToday.month, dToday.day) < (dBday.month, dBday.day))

    @api.one
    @api.depends('admission_date')
    def _compute_years_worked(self):
        if self.admission_date:
            dBday = datetime.strptime(self.admission_date, DEFAULT_SERVER_DATE_FORMAT).date()
            dToday = datetime.now().date()
            self.years_worked = dToday.year - dBday.year - ((dToday.month, dToday.day) < (dBday.month, dBday.day))

    @api.onchange('identification_id')
    def onchange_identification(self):
        if self.identification_id:
            if len(self.identification_id) < 11:
                raise ValidationError(_('The identification number must has 11 digits!'))

            self.gender = 'male' if not int(self.identification_id[len(self.identification_id) - 2]) % 2 else 'female'
            try:
                self.birthday = self._get_date_from_ci(self.identification_id)
            except Exception, e:
                pass

    def _get_date_from_ci(self, identification_id):
        if identification_id and len(identification_id) == 11:
            strdate = identification_id[:6]
            return datetime.strptime("19" + strdate if int(strdate[:2]) > 25 else "20" + strdate,
                                              "%Y%m%d").strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

    @api.onchange('job_id')
    def onchange_job_id(self):
        if self.job_id:
            self.department_id = self.job_id.department_id or False

    @api.one
    @api.constrains('name')
    def _check__name(self):
        valid_name_regexp = "^([ a-zA-ZáéíóúñÑÁÉÍÓÚÀÈÌÒÙàèìòù'.,\-])+$"

        if self.name:
            assert re.match(valid_name_regexp, self.name.encode('utf8')), 'Name has numbers'

    def getAttendanceCard(self, year, mes, shows_sat_sun):

        def getHoliday(employee_id, fecha_str):
            # verificar si hay peticion de holiday
            query = """SELECT id, holiday_status_id FROM hr_holidays WHERE employee_id = %s AND date_from::timestamp::date <= %s AND %s <= date_to::timestamp::date;"""
            self.env.cr.execute(query, (employee_id, fecha_str, fecha_str))
            query_results = self.env.cr.fetchone()
            valor = ''

            if query_results:
                valor = self.env['hr.holidays.status'].browse(query_results[1]).name

            return valor

        dateMonthStart = "%s-%s-01" % (year, mes)
        dateMonthEnd = "%s-%s-%s" % (year, mes, calendar.monthrange(year, int(mes))[1])

        start_date = datetime.strptime(dateMonthStart, DEFAULT_SERVER_DATE_FORMAT).date()
        end_date = datetime.strptime(dateMonthEnd, DEFAULT_SERVER_DATE_FORMAT).date()

        d = start_date
        delta = timedelta(days=1)
        # recorrer el intervalo de fecha
        list_dia = []
        i = 0
        s = 16
        while d <= end_date:
            date_to_process = datetime.strptime(d.strftime("%Y-%m-%d"), DEFAULT_SERVER_DATE_FORMAT)
            dayNomber = date_to_process.day
            day = str(datetime.isoweekday(date_to_process))
            value = ''
            if shows_sat_sun == True:
                if day == '6':
                    value = 'Sábado'
                if day == '7':
                    value = 'Domingo'
                if day != '6' and day != '7':
                    value = getHoliday(self.id, date_to_process.strftime(DEFAULT_SERVER_DATE_FORMAT))

                if i <= 15:
                    list_dia.append(dict(dias1=dayNomber, valors1=value, dias2='', valors2=''))
                else:
                    k = i - 16
                    list_dia[k]['dias2'] = dayNomber
                    list_dia[k]['valors2'] = value
            else:
                if day != '6' and day != '7':
                    value = getHoliday(self.id, date_to_process.strftime(DEFAULT_SERVER_DATE_FORMAT))
                if i <= 15:
                    list_dia.append(dict(dias1=dayNomber, valors1='', dias2='', valors2=''))
                else:
                    k = i - 16
                    list_dia[k]['dias2'] = dayNomber

            d += delta
            i += 1
        return list_dia

class EmployeeSchoolLevel(models.Model):
    _name = "l10n_cu_hlg_hr.employee_school_level"
    _description = "Employee School Level"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    external_id = fields.Char()


class EmployeeDefenseLocation(models.Model):
    _name = "l10n_cu_hlg_hr.employee_defence_location_type"
    _description = "Defence Location Type"

    code = fields.Char(required=True)
    name = fields.Char(string='Location', required=True)
    external_id = fields.Char()


class JobOccupationalCategory(models.Model):
    _name = 'l10n_cu_hlg_hr.occupational_category'
    _description = 'Employee Occupational Category'
    _order = 'order'

    order = fields.Integer()
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    external_id = fields.Char()

    _sql_constraints = [
        ('code', 'unique (code)', 'The code must be unique!')
    ]


class SalaryScale(models.Model):
    _name = 'l10n_cu_hlg_hr.salary_scale'
    _description = 'Salary Scale'

    name = fields.Char("Salary Scale", required=True)

    _sql_constraints = [
        ('name', 'unique (name)', 'The name must be unique!'),
    ]


class SalaryGroup(models.Model):
    _name = 'l10n_cu_hlg_hr.salary_group'
    _description = 'Salary Group'
    _rec_name = "salary_scale_id"

    scale_salary = fields.Float(string="Scale Salary")
    salary_scale_id = fields.Many2one('l10n_cu_hlg_hr.salary_scale', string='Salary Scale', required=True)
    external_id = fields.Char()

    occupational_category_id = fields.Many2one(
        'l10n_cu_hlg_hr.occupational_category', required=True, ondelete='restrict', string='Occupational Category'
    )

    _sql_constraints = [
        ('name', 'unique (name, occupational_category_id)', 'The name and occupational category  must be unique!')
    ]


class Position(models.Model):
    _name = 'l10n_cu_hlg_hr.position'
    _description = 'Position'

    name = fields.Char(string='Position Title', required=True, index=True, translate=True)
    salary_group_id = fields.Many2one('l10n_cu_hlg_hr.salary_group', string='Salary Group')
    salary = fields.Float(related='salary_group_id.scale_salary', string='Salary', readonly=True)
    school_level_id = fields.Many2one('l10n_cu_hlg_hr.employee_school_level', string='School Level')
    order= fields.Integer("Order")
    # Relateds
    occupational_category_id = fields.Many2one(
        related='salary_group_id.occupational_category_id', string='Occupational Category', readonly=True)


class Job(models.Model):
    _inherit = "hr.job"

    position_id = fields.Many2one('l10n_cu_hlg_hr.position', string='Position', required=False)
    code = fields.Char(string='Codigo')
    is_by_appointment = fields.Boolean(string='Job By Appointment?')

    school_level_id = fields.Many2one(
        related='position_id.school_level_id', string='School Level', store=True, readonly=True
    )

    salary_group_id = fields.Many2one(
        related='position_id.salary_group_id', string='Salary Group', store=True, readonly=True
    )

    occupational_category_id = fields.Many2one(
        related='position_id.salary_group_id.occupational_category_id', string='Occupational Category',
        store=True, readonly=True
    )


class Message(models.Model):
    _inherit = ['mail.message']

    @api.model
    def _get_default_from(self):
        if self.env.user.notify_email == 'always':
            if self.env.user.email:
                return formataddr((self.env.user.name, self.env.user.email))
            raise UserError(_("Unable to send email, please configure the sender's email address."))
