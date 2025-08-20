# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class EfficacyEvaluation(models.Model):
    _name = 'maintenance_turei.efficacy_evaluation'
    _description = 'Efficacy Evaluation'
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
    evaluation_parameter_id = fields.Many2one('maintenance_turei.evaluation_parameter', 'Parametro')
    # value_reached = fields.Integer('Valor alcanzado', compute='_compute_value_reached', store=True)
    # value_efficacy_industry = fields.Float('Puntuación para determinar si el proceso de mantenimiento es eficiente')
    # unit_value_efficacy_industry = fields.Selection(selection=[('>', '>'), ('<', '<'), ('>=', '>='), ('<=', '<=')], string='Operador para puntuación eficiente')
    # comp_value_efficacy_industry = fields.Char('Puntuación para determinar si el proceso de mantenimiento es eficiente', compute='_compute_value_efficacy_industry', store=True)

    # @api.model_create_multi
    # @api.depends('value_punctuation', 'value_weight')
    # def _compute_value_reached(self):
    #     for c_model in self:
    #         c_model.value_reached = c_model.value_punctuation * c_model.value_weight

    @api.depends('value_efficacy', 'unit_value_efficacy')
    def _compute_value_efficacy(self):
        for c_model in self:
            value_unit = c_model.unit_value_efficacy if c_model.unit_value_efficacy else ''
            c_model.comp_value_efficacy = '{} {}'.format(value_unit, c_model.value_efficacy)

    @api.depends('value_no_efficacy', 'unit_value_no_efficacy')
    def _compute_value_no_efficacy(self):
        for c_model in self:
            value_unit = c_model.unit_value_no_efficacy if c_model.unit_value_no_efficacy else ''
            c_model.comp_value_no_efficacy = '{} {}'.format(value_unit, c_model.value_no_efficacy)
