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


class CmiIndicator (models.Model):
    _inherit = 'cmi.indicator'

    type = fields.Selection(selection_add=[('survey', 'Survey')])

    @api.multi
    def _get_survey_values(self, indicator, params):
        obj = self.env['survey.user_input_line']
        value = {}
        if indicator.periodicity == 'monthly':
            start = date(params['year'], params['month'], 1)
            stop = ((start + relativedelta(months=1)) - relativedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            start = start.strftime(DEFAULT_SERVER_DATE_FORMAT)
            value = {'year': str(params['year']), 'month': int(params['month'])}
        elif indicator.periodicity == 'annual':
            start = date(params['year'], 1, 1)
            stop = ((start + relativedelta(years=1)) - relativedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            start = start.strftime(DEFAULT_SERVER_DATE_FORMAT)
            value = {'year': str(params['year'])}
        else:
            value = {'date': str(params['date'])}
            start = datetime.strptime(params[date], DEFAULT_SERVER_DATE_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
            stop = datetime.strptime(params[date], DEFAULT_SERVER_DATE_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)

        inputs = obj.search([('date_create', '>=', start), ('date_create', '<=', stop), ('question_id', 'in', indicator.source_id.question_ids.ids)])

        temp_value_max = 0
        temp_value_min = 99999999
        temp_value_sum = 0
        for inp in inputs:
            if indicator.source_id.aggregation in ('avg', 'sum'):
                temp_value_sum += self._get_input_value(inp)
            elif indicator.source_id.aggregation == 'min':
                temp_value_min = min(temp_value_min, self._get_input_value(inp))
            elif indicator.source_id.aggregation == 'max':
                temp_value_max = min(temp_value_max, self._get_input_value(inp))

        if indicator.source_id.aggregation == 'avg':
            value['value'] = float(temp_value_sum/len(inputs))
        elif indicator.source_id.aggregation == 'sum':
            value['value'] = temp_value_sum
        elif indicator.source_id.aggregation == 'min':
            value['value'] = temp_value_min
        elif indicator.source_id.aggregation == 'max':
            value['value'] = temp_value_max

        return [value]

    def _get_input_value(self, inp):
        if inp.answer_type == 'suggestion':
            return float(inp.value_suggested.value)
        else:
            return float(inp.value_number)

    @api.multi
    def _cron_recurring_extract_indicators(self, exe_date=False):
        all_indicators = self.env['cmi.indicator'].search(
            [('type', 'in', ('automatic', 'mixed_plan', 'mixed_real', 'survey'))])
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

                if indicator.source_id.type == 'survey':
                    values = self._get_survey_values(indicator, params)
                else:
                    if model:
                        values = self.env[model].get_values(params)
                    else:
                        values = []

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
                            company = self.env['res.company'].search([('code', '=', value['company_code'])],
                                                                     limit=1)
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
                        elif indicator.type == 'mixed_real' or indicator.type == 'survey':
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


class CmiSource(models.Model):
    _inherit = 'cmi.source'

    model = fields.Many2one('ir.model', 'Model', required=False, domain="[('field_id.name', '=', 'cmi_source')]")
    type = fields.Selection(selection_add=[('survey', 'Survey')])
    aggregation = fields.Selection(string="Aggregation",
                                   selection=[('sum', 'Sum'), ('avg', 'Avg'), ('max', 'Max'), ('min', 'Min')],
                                   required=True, default='avg')
    survey_id = fields.Many2one(
        comodel_name='survey.survey',
        string='Survey')
    question_ids = fields.Many2many(
        comodel_name='survey.question',
        string='Questions', domain="[('survey_id', '=', survey_id), ('type', 'in', ['matrix', 'numerical_box', 'simple_choice'])]")





    


