# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class EvaluationParameter(models.Model):
    _name = 'maintenance_turei.evaluation_parameter'
    _description = 'Evaluation Parameter'
    _rec_name = 'cohef_maint'

    cohef_maint = fields.Float('Coheficiente de eficacia del proceso de mantenimiento')
    unit_cohef_maint = fields.Selection(selection=[('>', '>'), ('<', '<'), ('>=', '>='), ('<=', '<=')], string='Operador Eficaz')
    comp_value_efficacy_industry = fields.Char('Puntuación para determinar si el proceso de mantenimiento es eficiente', compute='_compute_value_efficacy_industry', store=True)
    value_opt = fields.Float('Valor Óptimo Alcanzado', default=65.00)
    efficacy_evaluation_ids = fields.One2many(comodel_name='maintenance_turei.efficacy_evaluation', inverse_name='evaluation_parameter_id', string='Indicadores')

    @api.depends('cohef_maint', 'unit_cohef_maint')
    def _compute_value_efficacy_industry(self):
        for c_model in self:
            value_unit = c_model.unit_cohef_maint if c_model.unit_cohef_maint else ''
            c_model.comp_value_efficacy_industry = '{} {}'.format(value_unit, c_model.cohef_maint)