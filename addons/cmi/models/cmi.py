# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import json
from odoo.tools.translate import _
import logging
from datetime import datetime, date, timedelta
from sys import platform
import os
import subprocess

_logger = logging.getLogger(__name__)


class CmiUOM(models.Model):
    _name = 'cmi.uom'
    _rec_name = 'name'
    _description = 'Indicator Unit of Measure'

    name = fields.Char('Name', size=256, required=True)
    abbreviated_name = fields.Char('Short Name', size=20, required=True)


class CmiSource(models.Model):
    _name = 'cmi.source'
    _rec_name = 'name'
    _description = 'Represent a model responsible for calculating the values of an indicator'

    name = fields.Char(size=256, required=True)
    model = fields.Many2one('ir.model', 'Model', required=True, domain="[('field_id.name', '=', 'cmi_source')]")
    type = fields.Selection(string="Type",
                            selection=[('manual', 'Manual'), ('mixed_plan', 'Mixed(Plan)'),
                                       ('mixed_real', 'Mixed(Real)'), ('automatic', 'Automatic')],
                            required=True)


class CmiPerspective(models.Model):
    _name = 'cmi.perspective'
    _rec_name = 'name'
    _description = "Perspectives of evaluation of the company's performance"

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get('cmi.indicator')
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    name = fields.Char(size=256, required=True)
    priority = fields.Integer(string="Priority", required=True)
    indicator_ids = fields.One2many(comodel_name="cmi.indicator", inverse_name="perspective_id", string="Indicators",
                                    required=False, )


class CmiIndicator(models.Model):
    _name = 'cmi.indicator'
    _rec_name = 'name'
    _description = "Company's performance indicator"
    _inherit = ["mail.thread"]

    @api.multi
    def action_follow(self):
        """ Wrapper because message_subscribe_users take a user_ids=None
            that receive the context without the wrapper.
        """
        return self.message_subscribe_users()

    @api.multi
    def action_unfollow(self):
        """ Wrapper because message_unsubscribe_users take a user_ids=None
            that receive the context without the wrapper.
        """
        return self.message_unsubscribe_users()

    @api.depends('line_ids', 'value_type', 'optimal_value', 'maximum_limit', 'lower_limit', 'medium_limit',
                 'uom_abbreviated_name')
    @api.multi
    def _compute_fields(self):
        for record in self:
            if len(record.line_ids):
                if 'filter_period' in self.env.context:
                    domain = [['indicator_id', '=', record.id]]
                    domain.extend(self.env.context.get('filter_period'))
                    record.last_value = self.env['cmi.indicator.line'].search(domain, limit=1)
                else:
                    record.last_value = record.line_ids[0].id

                if record.last_value:
                    record.date_string = record.last_value.date_string
                    # calculate value
                    if record.value_type == 'percentage':
                        record.value = (
                                               record.last_value.value * 100.00) / record.last_value.plan if record.last_value.plan else 0.00
                        record.gauge_uom = '%'
                    elif record.value_type == 'yes_no':
                        record.value = 100 if record.last_value.value > 0.00 else 0
                        record.gauge_uom = '%'
                    else:
                        record.value = record.last_value.value
                        record.gauge_uom = record.uom_abbreviated_name

                    # compute color
                    if record.optimal_value == 'max':
                        if record.lower_limit < record.value <= record.medium_limit:
                            record.color = 'yellow'
                        elif record.lower_limit >= record.value:
                            record.color = 'red'
                        else:
                            record.color = 'green'
                    elif record.optimal_value == 'min':
                        if record.lower_limit < record.value <= record.medium_limit:
                            record.color = 'yellow'
                        elif record.lower_limit >= record.value:
                            record.color = 'green'
                        else:
                            record.color = 'red'
                    else:
                        if record.lower_limit < record.value <= record.medium_limit:
                            record.color = 'green'
                        else:
                            record.color = 'red'

                    # calculate zones limit
                    record.first_zone_limit = record.lower_limit / record.maximum_limit if record.maximum_limit else 0.00
                    record.second_zone_limit = record.medium_limit / record.maximum_limit if record.maximum_limit else 0.00

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get('cmi.indicator')
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    uom_id = fields.Many2one(comodel_name="cmi.uom", string="Unit of Measure", required=False)
    responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible", required=True)
    name = fields.Char(size=256, required=True)
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(string="",
                             selection=[('deficient', 'Deficient'), ('regular', 'Regular'), ('good', 'Good')],
                             required=False)
    type = fields.Selection(string="Type",
                            selection=[('manual', 'Manual'), ('mixed_plan', 'Mixed(Plan)'),
                                       ('mixed_real', 'Mixed(Real)'), ('automatic', 'Automatic')],
                            required=True)
    aggregation = fields.Selection(string="Aggregation",
                                   selection=[('sum', 'Sum'), ('avg', 'Avg'), ('max', 'Max'), ('min', 'Min')],
                                   required=True, default='sum')
    consolidated = fields.Boolean('Consolidated', required=True, default=True)
    value_type = fields.Selection(string="Value Type",
                                  selection=[('percentage', 'Percentage'), ('unique', 'Unique Value'),
                                             ('yes_no', 'Yes/No')],
                                  required=True)
    optimal_value = fields.Selection(string="Optimal Value",
                                     selection=[('min', 'Minimum Possible'), ('max', 'Maximum Possible'),
                                                ('range', 'Range')],
                                     required=True, default='max')
    char_type = fields.Selection(string="Chart Type",
                                 selection=[('bar', 'Bar Chart'), ('line', 'Line Chart')],
                                 # selection=[('bar', 'Bar Chart'), ('pie', 'Pie Chart'), ('line', 'Line Chart')],
                                 required=False)
    periodicity = fields.Selection(string="",
                                   selection=[('daily', 'Daily'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'),
                                              ('semiannual', 'Semiannual'), ('annual', 'Annual')],
                                   required=True)
    lower_limit = fields.Float(string="Lower Limit", required=False)
    medium_limit = fields.Float(string="Medium Limit", required=False)
    maximum_limit = fields.Float(string="Maximum Limit", required=False, default=100)
    source_id = fields.Many2one(comodel_name="cmi.source", string="Data Source", required=False,
                                domain="[('type', '=', type)]")
    perspective_id = fields.Many2one(comodel_name="cmi.perspective", string="Perspective", required=False)
    line_ids = fields.One2many(comodel_name="cmi.indicator.line", inverse_name="indicator_id", string="Indicator lines",
                               required=False)
    last_value = fields.Many2one(comodel_name="cmi.indicator.line", string="Last Value", required=False,
                                 compute=_compute_fields, search='_search_compute')
    value = fields.Float(compute=_compute_fields, string="Value", required=False)
    first_zone_limit = fields.Float(compute=_compute_fields, string="First Zone Limit", required=False)
    second_zone_limit = fields.Float(compute=_compute_fields, string="Second Zone Limit", required=False)
    date_string = fields.Char(compute=_compute_fields, string="Date", required=False)
    gauge_uom = fields.Char(compute=_compute_fields, string="Gauge Uom", required=False)
    plan = fields.Float(related='last_value.plan', string="Plan", required=False)
    real = fields.Float(related='last_value.value', string="Real", required=False)
    month = fields.Selection(related='last_value.month', required=False)
    date = fields.Date(related='last_value.date', required=False)
    # trimester = fields.Selection(related='last_value.trimester', required=False)
    # semester = fields.Selection(related='last_value.semester', required=False)
    year = fields.Selection(related='last_value.year', required=False)
    # total = fields.Float(related='last_value.total', string="Plan", required=False)
    color = fields.Char(string="Color", required=False, compute=_compute_fields)
    uom_abbreviated_name = fields.Char(related='uom_id.abbreviated_name')

    @api.multi
    def _cron_recurring_extract_indicators(self, exe_date=False):
        all_indicators = self.env['cmi.indicator'].search([('type', 'in', ('automatic', 'mixed_plan', 'mixed_real'))])
        line_obj = self.env['cmi.indicator.line']
        today = datetime.today()
        for indicator in all_indicators:
            model = indicator.source_id.model.model
            aux_date = datetime.strptime(exe_date, DEFAULT_SERVER_DATE_FORMAT) if exe_date else today
            delta = relativedelta(days=1)
            if indicator.periodicity == 'monthly':
                delta = relativedelta(months=1)
            elif indicator.periodicity == 'quarterly':
                delta = relativedelta(months=3)
            elif indicator.periodicity == 'semiannual':
                delta = relativedelta(months=6)
            elif indicator.periodicity == 'annual':
                delta = relativedelta(years=1)
            while aux_date <= today:
                params = {'year': aux_date.year, 'month': aux_date.month,
                          'date': aux_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
                          'trimester': int(aux_date.month / 3) + (1 if aux_date.month % 3 > 0 else 0),
                          'semester': int(aux_date.month / 6) + (1 if aux_date.month % 6 > 0 else 0),
                          'consolidated': indicator.consolidated}
                values = self.env[model].get_values(params)
                if values and len(values):
                    data = {'indicator_id': indicator.id}
                    for value in values:

                        domain = [('indicator_id', '=', indicator.id)]
                        if indicator.periodicity == 'daily':
                            domain.append(('date', '=', value['date']))
                        elif indicator.periodicity == 'monthly':
                            domain.append(('year', '=', str(value['year'])))
                            domain.append(('month', '=', "%02d" % value['month']))
                        elif indicator.periodicity == 'quarterly':
                            domain.append(('year', '=', str(value['year'])))
                            domain.append(('trimester', '=', str(value['trimester'])))
                        elif indicator.periodicity == 'semiannual':
                            domain.append(('year', '=', str(value['year'])))
                            domain.append(('semester', '=', str(value['semester'])))
                        elif indicator.periodicity == 'annual':
                            domain.append(('year', '=', str(value['year'])))

                        if 'company_code' in value:
                            company = self.env['res.company'].search([('code', '=', value['company_code'])], limit=1)
                            if not len(company):
                                raise ValidationError(_("""There are no companies with the specified code"""))
                            else:
                                company_id = company.id
                        else:
                            company_id = self._default_company_id().id

                        data.update({'company_id': company_id})
                        domain.append(('company_id', '=', company_id))
                        data_update = {}
                        if indicator.periodicity == 'daily':
                            data_update['date'] = value['date']
                        elif indicator.periodicity == 'monthly':
                            data_update['year'] = str(value['year'])
                            data_update['month'] = "%02d" % int(value['month'])
                        elif indicator.periodicity == 'quarterly':
                            data_update['year'] = str(value['year'])
                            data_update['trimester'] = str(value['trimester'])
                        elif indicator.periodicity == 'semiannual':
                            data_update['year'] = str(value['year'])
                            data_update['semester'] = str(value['semester'])
                        if indicator.type == 'automatic':
                            data_update['plan'] = value['plan']
                            data_update['value'] = value['value']
                        elif indicator.type == 'mixed_real':
                            data_update['value'] = value['value']
                        elif indicator.type == 'mixed_plan':
                            data_update['plan'] = value['plan']
                        data_update.update(data)

                        current = line_obj.search(domain)
                        if len(current):
                            current.update(data_update)
                        else:
                            line_obj.create(data_update)

                aux_date = aux_date + delta

    @api.multi
    def _cron_execute_transformations(self, exe_date=False):
        companies = self.env['res.company'].search(
            [('dw_conn_id', '!=', False), ('job_dir', '!=', False), ('pdi_dir', '!=', False)])
        if platform == 'linux2':
            spoon_file = 'kitchen.sh'
        elif platform == 'win32':
            spoon_file = 'Kitchen.bat'
        for company in companies:
            if os.path.exists(company.pdi_dir + os.sep + spoon_file) and os.path.isfile(
                    company.pdi_dir + os.sep + spoon_file) and os.path.exists(company.job_dir) and os.path.isfile(
                company.job_dir):
                try:
                    if exe_date:
                        subprocess.call(
                            [company.pdi_dir + os.sep + spoon_file, " -param:FECHAACTUAL=%s " % exe_date, "/file",
                             company.job_dir, "/maxloglines", "1000"],
                            cwd=company.pdi_dir)
                    else:
                        subprocess.call([company.pdi_dir + os.sep + spoon_file, "/file", company.job_dir, "/maxloglines", "1000"], cwd=company.pdi_dir)
                    self._cron_recurring_extract_indicators(exe_date)
                except Exception as e:
                    _logger.warning(e.message)
        return

    @api.multi
    def _cron_send_indicators_state(self):
        companies = self.env['res.company'].search([])
        for company in companies:
            if company.email_list:
                indicators_state_template = self.env.ref('cmi.email_template_indicators_state')
                rendering_context = dict(self._context)
                rendering_context.update({
                    'active_company_id': company.id,
                })
                indicators_state_template = indicators_state_template.with_context(rendering_context)
                indicators_state_template.send_mail(company.id, False, False, {'email_to': company.email_list})

    @api.constrains('lower_limit', 'medium_limit', 'maximum_limit')
    def _check_evaluation_attrs(self):
        for indicator in self:
            if indicator.lower_limit > indicator.medium_limit:
                raise ValidationError(_('Error! Lower limit can not be higher than the Medium limit.'))
            if indicator.lower_limit > indicator.maximum_limit:
                raise ValidationError(_('Error! Lower limit can not be higher than the Maximum limit.'))
            if indicator.medium_limit > indicator.maximum_limit:
                raise ValidationError(_('Error! Medium limit can not be higher than the Maximum limit.'))

    @api.model
    def create(self, values):
        if values.get('value_type') == 'yes_no':
            values['lower_limit'] = 0.5
            values['medium_limit'] = 0.5
            values['maximum_limit'] = 100.0
        return super(CmiIndicator, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('value_type') == 'yes_no':
            values['lower_limit'] = 0.5
            values['medium_limit'] = 0.5
            values['maximum_limit'] = 1.0
        return super(CmiIndicator, self).write(values)

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        new_args = []
        lines_domain = []
        dict_lines_domain = {}
        context = {}
        context.update(self.env.context)
        for arg in args:
            if arg[0] == 'date':
                dict_lines_domain[arg[0]] = arg
        ids = []
        if len(dict_lines_domain):
            lines_domain = self._get_period_domain(dict_lines_domain)
            context['filter_period'] = lines_domain
            lines = self.env['cmi.indicator.line'].search_read(lines_domain, ['indicator_id'])
            if len(lines):
                ids = map(lambda x: x['indicator_id'][0], lines)

        for arg in args:
            new_arg = arg
            if arg[0] == 'date':
                new_args.append(['id', 'in', ids])
            else:
                new_args.append(new_arg)

        if count:
            return super(CmiIndicator, self).search(new_args, offset=offset, limit=limit, order=order, count=count)
        else:
            return super(CmiIndicator, self).search(new_args, offset=offset, limit=limit, order=order,
                                                    count=count).with_context(context)

    @api.multi
    def _search_compute(self, operator, value):
        return []

    def _get_period_domain(self, filters):
        domain = []
        if 'date' in filters:
            date_filter = datetime.strptime(filters['date'][2], DEFAULT_SERVER_DATE_FORMAT).date()
            year = date_filter.year
            month = date_filter.month
            trimester = int(month / 3) + (1 if month % 3 > 0 else 0)
            semester = int(month / 6) + (1 if month % 6 > 0 else 0)
            domain += ['|', ('date', '=', filters['date'][2]), '&', ('year', '=', str(year)), '|', '|',
                       ('month', '=', "%02d" % month), ('trimester', '=', trimester), ('semester', '=', semester)]
        return domain

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields_to_hide = ['__last_update', 'create_date', 'create_uid', 'message_needaction', 'create_uid',
                          'message_follower_ids', 'message_channel_ids', 'message_partner_ids', 'last_value', 'plan',
                          'real', 'write_date', 'write_uid', 'message_last_post', 'message_ids', 'message_is_follower',
                          'line_ids', 'uom_abbreviated_name', 'year', 'month']
        res = super(CmiIndicator, self).fields_get(allfields, attributes)
        for field in fields_to_hide:
            res[field]['selectable'] = False
        return res


class CmiIndicatorLine(models.Model):
    _name = 'cmi.indicator.line'
    _rec_name = 'indicator_id'
    _description = 'Line of result of an indicator'
    _order = 'year desc, semester desc, trimester desc, month desc, date desc'

    @api.model
    def _default_year(self):
        today = date.today()
        today_list = str(today).split('-')
        return today_list[0]

    def default_year(self):
        today = str(date.today()).split('-')
        year_list = []
        for i in range(int(today[0]) - 35, int(today[0]) + 35):
            pair = (str(i), str(i))
            year_list.append(pair)
        return year_list

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get('cmi.indicator')
        return company_id

    @api.depends('date', 'year', 'month', 'semester', 'trimester')
    @api.multi
    def _compute_date_string(self):
        for record in self:
            record.date_string = ''
            if record.periodicity == 'daily' and record.date:
                record.date_string = (datetime.strptime(record.date, DEFAULT_SERVER_DATE_FORMAT).date()).strftime(
                    '%d/%m/%Y')
            elif record.periodicity == 'monthly' and record.month:
                month = dict(
                    self.env['cmi.indicator.line'].fields_get(allfields=['month'])['month']['selection'])[
                    record.month]
                record.date_string = month + ' ' + record.year
            elif record.periodicity == 'quarterly' and record.trimester:
                trimester = dict(
                    self.env['cmi.indicator.line'].fields_get(allfields=['trimester'])['trimester']['selection'])[
                    record.trimester]
                record.date_string = trimester + ' ' + _('Trimester') + ' ' + record.year
            elif record.periodicity == 'semiannual' and record.semester:
                semester = dict(
                    self.env['cmi.indicator.line'].fields_get(allfields=['semester'])['semester']['selection'])[
                    record.semester]
                record.date_string = semester + ' ' + _('Semester') + ' ' + record.year
            elif record.periodicity == 'annual' and record.year:
                record.date_string = record.year

    name = fields.Char(related='indicator_id.name')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    value_type = fields.Selection(related='indicator_id.value_type')
    type = fields.Selection(related='indicator_id.type')
    periodicity = fields.Selection(related='indicator_id.periodicity')
    # total = fields.Float(string="Total", required=False)
    plan = fields.Float(string="Plan", required=False)
    value = fields.Float(string="Real", required=False)
    date = fields.Date(string='Date', required=False, default=lambda self: fields.datetime.today(), index=True)
    month = fields.Selection(string="Month",
                             selection=[('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                                        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                                        ('09', 'September'), ('10', 'October'), ('11', 'November'),
                                        ('12', 'December')],
                             required=False, index=True)
    trimester = fields.Selection(string="Trimester", selection=[('1', 'I'), ('2', 'II'), ('3', 'III'), ('4', 'IV'), ],
                                 required=False, index=True)
    semester = fields.Selection(string="Semester", selection=[('1', 'I'), ('2', 'II'), ], required=False, index=True)
    year = fields.Selection(default_year, string='Year', required=False, default=_default_year, index=True)
    indicator_id = fields.Many2one(comodel_name="cmi.indicator", string="Indicator", required=True, ondelete='cascade',
                                   index=True)
    date_string = fields.Char(compute=_compute_date_string, string="Date", required=False)


class CmiDashboard(models.Model):
    _name = 'cmi.dashboard'
    _rec_name = 'name'
    _description = 'DashBoard to show indicators'

    @api.one
    def _default_year(self):
        today = date.today()
        today_list = str(today).split('-')
        self.year = today_list[0]

    def default_year(self):
        today = str(date.today()).split('-')
        year_list = []
        for i in range(int(today[0]) - 35, int(today[0]) + 35):
            pair = (str(i), str(i))
            year_list.append(pair)
        return year_list

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get('cmi.indicator')
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    year = fields.Selection(default_year, string='Year', required=True, compute=_default_year)
    month = fields.Selection(string="Month",
                             selection=[('00', 'None'), ('01', 'January'), ('02', 'February'), ('03', 'March'),
                                        ('04', 'April'),
                                        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                                        ('09', 'September'), ('10', 'October'), ('11', 'November'),
                                        ('12', 'December')], default='00', required=True)
    name = fields.Char(size=256, required=True)
    indicator_ids = fields.Many2many(comodel_name="cmi.indicator", relation="cmi_dashboard_indicator_rel",
                                     column1="dashboard_id", column2="indicator_id", string="Indicators",
                                     domain="[('char_type' , '!=', False), ('char_type' , '!=', '')]")
    dashboard = fields.Text(string='Dashboard', compute='_compute_dashboard')

    @api.depends('year', 'month', 'indicator_ids')
    @api.one
    def _compute_dashboard(self):
        self.dashboard = json.dumps(self.get_dashboard_data())

    def get_dashboard_data(self):
        indicators = []
        MONTH = {'1': _('January'), '2': _('February'), '3': _('March'), '4': _('April'),
                 '5': _('May'), '6': _('June'), '7': _('July'), '8': _('August'),
                 '9': _('September'), '10': _('October'), '11': _('November'),
                 '12': _('December')}
        TRIMESTER = {'1': _('I'), '2': _('II'), '3': _('III'), '4': _('IV')}
        SEMESTER = {'1': _('I'), '2': _('II')}

        line_object = self.env['cmi.indicator.line']
        for indicator_id in self.indicator_ids:
            YEAR = {}
            DAYS = {}
            day = 1
            if indicator_id.periodicity == 'daily':
                if self.month and self.month != '00':
                    date_start = datetime(int(self.year), int(self.month), 1)
                    date_end = (date_start + relativedelta(months=1)) - relativedelta(days=1)
                else:
                    date_start = datetime(int(self.year), 1, 1)
                    date_end = datetime(int(self.year), 12, 31)

                lines = line_object.search([('indicator_id', '=', indicator_id.id),
                                            ('date', '>=', date_start.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                            ('date', '<=', date_end.strftime(DEFAULT_SERVER_DATE_FORMAT))],
                                           order='date asc')
            else:
                if self.month and self.month != '00':
                    trimester = int(int(self.month) / 3) + (1 if int(self.month) % 3 > 0 else 0)
                    semester = int(int(self.month) / 6) + (1 if int(self.month) % 6 > 0 else 0)
                    lines = line_object.search(
                        [('indicator_id', '=', indicator_id.id), ('year', '=', self.year), '|', '|',
                         ('month', '=', self.month), ('trimester', '=', str(trimester)),
                         ('semester', '=', str(semester))],
                        order='month asc, trimester asc, semester asc')
                else:
                    lines = line_object.search([('indicator_id', '=', indicator_id.id), ('year', '=', self.year)],
                                               order='month asc, trimester asc, semester asc')
            values = []
            plan = []
            for line in lines:
                if line.periodicity == 'daily':
                    label = (datetime.strptime(line.date, DEFAULT_SERVER_DATE_FORMAT).date()).strftime('%d/%m/%Y')
                    key = day
                    DAYS[day] = label
                    day += 1
                elif line.periodicity == 'monthly':
                    label = dict(
                        self.env['cmi.indicator.line'].fields_get(allfields=['month'])['month']['selection'])[
                        line.month]
                    key = line.month
                elif line.periodicity == 'quarterly':
                    label = dict(
                        self.env['cmi.indicator.line'].fields_get(allfields=['trimester'])['trimester']['selection'])[
                        line.trimester]
                    key = line.trimester
                elif line.periodicity == 'semiannual':
                    label = dict(
                        self.env['cmi.indicator.line'].fields_get(allfields=['semester'])['semester']['selection'])[
                        line.semester]
                    key = line.semester
                else:
                    label = line.year
                    key = line.year
                    YEAR[str(line.year)] = str(line.year)

                values.append({'value': line.value, 'key': key, 'label': label})
                plan.append({'value': line.plan, 'key': key, 'label': label})

            if indicator_id.periodicity == 'daily':
                ticks = DAYS
            elif indicator_id.periodicity == 'monthly':
                ticks = MONTH
            elif indicator_id.periodicity == 'quarterly':
                ticks = TRIMESTER
            elif indicator_id.periodicity == 'semiannual':
                ticks = SEMESTER
            else:
                ticks = YEAR

            if indicator_id.char_type == 'bar':
                indicators.append(
                    {'indicator': indicator_id.name, 'indicator_id': 'cmi_indicator_' + str(indicator_id.id),
                     'data': [{'key': _('Real'), 'values': values}, {'key': _('Plan'), 'values': plan}],
                     'chart_type': indicator_id.char_type})
            elif indicator_id.char_type == 'line':
                indicators.append(
                    {'indicator': indicator_id.name, 'indicator_id': 'cmi_indicator_' + str(indicator_id.id),
                     'data': [{'key': _('Real'), 'values': values}, {'key': _('Plan'), 'values': plan}],
                     'chart_type': indicator_id.char_type, 'ticks': ticks})
            else:
                indicators.append(
                    {'indicator': indicator_id.name, 'indicator_id': 'cmi_indicator_' + str(indicator_id.id),
                     'data': values,
                     'chart_type': indicator_id.char_type})

        return indicators
