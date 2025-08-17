# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class EvaluationParameter(models.Model):
    _name = 'turei_maintenance.evaluation_parameter'
    _rec_name = 'cohef_maint'

    cohef_maint = fields.Float('Coheficiente de eficacia del proceso de mantenimiento')
    unit_cohef_maint = fields.Selection(selection=[('>', '>'), ('<', '<'), ('>=', '>='), ('<=', '<=')], string='Operador Eficaz')
    comp_value_efficacy_industry = fields.Char('Puntuación para determinar si el proceso de mantenimiento es eficiente', compute='_compute_value_efficacy_industry', store=True)
    value_opt = fields.Float('Valor Óptimo Alcanzado', default=65.00)
    efficacy_evaluation_ids = fields.One2many(comodel_name='turei_maintenance.efficacy_evaluation', inverse_name='evaluation_parameter_id', string='Indicadores')

    @api.multi
    @api.depends('cohef_maint', 'unit_cohef_maint')
    def _compute_value_efficacy_industry(self):
        for c_model in self:
            value_unit = c_model.unit_cohef_maint if c_model.unit_cohef_maint else ''
            c_model.comp_value_efficacy_industry = '{} {}'.format(value_unit, c_model.cohef_maint)


class EfficacyEvaluation(models.Model):
    _name = 'turei_maintenance.efficacy_evaluation'
    # _rec_name = 'indicator'

    name = fields.Char('Indicador')
    value_opt = fields.Integer('Valor Óptimo', default=100)
    value_efficacy = fields.Float('Eficaz')
    unit_value_efficacy = fields.Selection(selection=[('>', '>'), ('<', '<'), ('>=', '>='), ('<=', '<=')], string='Operador Eficaz')
    comp_value_efficacy = fields.Char('Eficaz', compute='_compute_value_efficacy', store=True)
    value_no_efficacy = fields.Float('No Eficaz')
    unit_value_no_efficacy = fields.Selection(selection=[('>', '>'), ('<', '<'), ('>=', '>='), ('<=', '<=')], string='Operador No Eficaz')
    comp_value_no_efficacy = fields.Char('No Eficaz', compute='_compute_value_no_efficacy', store=True)
    # value_punctuation = fields.Integer('Puntuación', default=5)
    value_weight = fields.Integer('Peso', default=5)
    evaluation_parameter_id = fields.Many2one('turei_maintenance.evaluation_parameter', 'Parametro')
    # value_reached = fields.Integer('Valor alcanzado', compute='_compute_value_reached', store=True)
    # value_efficacy_industry = fields.Float('Puntuación para determinar si el proceso de mantenimiento es eficiente')
    # unit_value_efficacy_industry = fields.Selection(selection=[('>', '>'), ('<', '<'), ('>=', '>='), ('<=', '<=')], string='Operador para puntuación eficiente')
    # comp_value_efficacy_industry = fields.Char('Puntuación para determinar si el proceso de mantenimiento es eficiente', compute='_compute_value_efficacy_industry', store=True)

    # @api.multi
    # @api.depends('value_punctuation', 'value_weight')
    # def _compute_value_reached(self):
    #     for c_model in self:
    #         c_model.value_reached = c_model.value_punctuation * c_model.value_weight

    @api.multi
    @api.depends('value_efficacy', 'unit_value_efficacy')
    def _compute_value_efficacy(self):
        for c_model in self:
            value_unit = c_model.unit_value_efficacy if c_model.unit_value_efficacy else ''
            c_model.comp_value_efficacy = '{} {}'.format(value_unit, c_model.value_efficacy)

    @api.multi
    @api.depends('value_no_efficacy', 'unit_value_no_efficacy')
    def _compute_value_no_efficacy(self):
        for c_model in self:
            value_unit = c_model.unit_value_no_efficacy if c_model.unit_value_no_efficacy else ''
            c_model.comp_value_no_efficacy = '{} {}'.format(value_unit, c_model.value_no_efficacy)
