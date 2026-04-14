# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import fields, models, tools, api

class TemplateStageWear(models.Model):
    _name = "l10n_cu_hlg_hr_defense_inf.template_wear"
    _rec_name = 'position_id'

    position_id = fields.Many2one('l10n_cu_hlg_hr.position', string='Position', required=True)
    number_of_places = fields.Integer('Number of places', required=True)
    time_in_days = fields.Integer('Time in days')


class TemplateStageInvasion(models.Model):
    _name = "l10n_cu_hlg_hr_defense_inf.template_invasion"
    _rec_name = 'position_id'

    position_id = fields.Many2one('l10n_cu_hlg_hr.position', string='Position', required=True)
    number_of_places = fields.Integer('Number of places', required=True)
    time_in_days = fields.Integer('Time in days')
