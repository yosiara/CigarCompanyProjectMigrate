# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ProcessEfficacyLine(models.Model):
    _name = 'enterprise_mgm_sys.process_efficacy_line'

    process_efficacy_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.process_efficacy',
        string='Process_efficacy_id',
        required=True, ondelete='cascade')
    indicator_id = fields.Many2one(comodel_name='cmi.indicator', string='Indicator', required=True)
    evaluation = fields.Float(string='Evaluation', required=True, defualt=0)
    punctuation = fields.Integer(string='Punctuation', compute='_calc_values', required=True, store=True)
    weight = fields.Integer(string='Weight', compute='_calc_values', required=True, store=True)
    value_reached = fields.Integer(string='Value Reached', compute='_calc_values', required=True, store=True)
    optimal_value = fields.Integer(string='Optimal Value', compute='_calc_values', required=True, store=True)

    @api.depends('process_efficacy_id', 'indicator_id', 'evaluation')
    def _calc_values(self):
        for record in self:
            line = self.env['enterprise_mgm_sys.process_indicator_line'].search(
                [('process_id', '=', record.process_efficacy_id.process_id.id),
                 ('indicator_id', '=', record.indicator_id.id)], limit=1)

            if line:
                record.weight = line.weight
                if line.optimal_value == 'max':
                    if line.limit <= record.evaluation:
                        record.punctuation = line.points_effective
                    else:
                        record.punctuation = line.points_no_effective
                elif line.optimal_value == 'min':
                    if line.limit >= record.evaluation:
                        record.punctuation = line.points_effective
                    else:
                        record.punctuation = line.points_no_effective
                record.value_reached = record.punctuation * record.weight
                record.optimal_value = line.points_effective * record.weight
        return True


class ProcessEfficacy(models.Model):
    _name = 'enterprise_mgm_sys.process_efficacy'
    _rec_name = 'process_id'

    process_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.process',
        string='Process',
        required=True)
    line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.process_efficacy_line',
        inverse_name='process_efficacy_id',
        string='Evaluations',
        required=True)
    month = fields.Selection(string="Month",
                             selection=[('01', 'January'), ('02', 'February'), ('03', 'March'),
                                        ('04', 'April'),
                                        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                                        ('09', 'September'), ('10', 'October'), ('11', 'November'),
                                        ('12', 'December')], default=lambda month: '%02d' % datetime.today().month, required=True)
    year = fields.Char(string='Year', required=True, default=lambda year: str(datetime.today().year))
    expedition_date = fields.Date(string='Expedition date', required=True, default=lambda today: datetime.today())
    real_value = fields.Integer(string='Real value', compute='_compute_values', store=True, group_operator="avg")
    total = fields.Float(string='Total(%)', compute='_compute_values', store=True, group_operator="avg")
    optimal_value = fields.Integer(string='Optimal value', compute='_compute_values', store=True, group_operator="avg")
    efficacy = fields.Selection(
        string='Efficacy',
        selection=[('efficacious', 'Efficacious'),
                   ('no_efficacious', 'No efficacious'), ], compute='_compute_values', store=True)

    @api.depends('line_ids')
    def _compute_values(self):
        for record in self:
            real_value = 0
            optimal_value = 0
            for line in record.line_ids:
                real_value += line.value_reached
                optimal_value += line.optimal_value

            if optimal_value:
                record.total = (real_value * 100.00) / optimal_value
                record.real_value = real_value
                record.optimal_value = optimal_value
                record.efficacy = 'efficacious' if record.total >= record.process_id.limit else 'no_efficacious'

    @api.onchange('process_id', 'year', 'month')
    def _onchange_process_id(self):
        list = [(6, 0, [])]
        if self.process_id and self.month and self.year:
            for line in self.process_id.indicator_ids:
                year = int(self.year)
                month = int(self.month)
                trimester = int(int(month) / 3) + (1 if int(month) % 3 > 0 else 0)
                semester = int(int(month) / 6) + (1 if int(month) % 6 > 0 else 0)
                temp_date = ((datetime(year, month, 1) + relativedelta(months=1)) - relativedelta(days=1)).date().strftime(DEFAULT_SERVER_DATE_FORMAT)
                domain = [('indicator_id', '=', line.indicator_id.id), '|', ('date', '=', temp_date), '&', ('year', '=', self.year), '|', '|',
                           ('month', '=', self.month), ('trimester', '=', str(trimester)), ('semester', '=', str(semester))]
                record_value = self.env['cmi.indicator.line'].search(domain, limit=1)
                evaluation = 0.0
                if record_value:
                    if line.indicator_id.value_type == 'percentage':
                        evaluation = (record_value.value * 100.00) / record_value.plan if record_value.plan else 0.00
                    elif line.indicator_id.value_type == 'yes_no':
                        evaluation = 100 if record_value.value > 0.00 else 0
                    else:
                        evaluation = record_value.value

                list.append((0, 0, {
                    'indicator_id': line.indicator_id.id,
                    'evaluation': evaluation
                }))

        return {'value': {'line_ids': list}}

