# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProcessIndicatorLine(models.Model):
    _name = 'enterprise_mgm_sys.process_indicator_line'
    _rec_name = 'indicator_id'

    process_id = fields.Many2one(comodel_name='enterprise_mgm_sys.process', string='Process', required=True, ondelete='cascade')
    indicator_id = fields.Many2one(comodel_name='cmi.indicator', string='Indicator', required=True)
    points_effective = fields.Integer(string='Points effective', required=True)
    points_no_effective = fields.Integer(string='Points no effective', required=True)
    weight = fields.Integer(string='Weight', required=True)
    limit = fields.Float(string="Lower Limit", required=True)
    optimal_value = fields.Selection(string="Optimal Value",
                                     selection=[('min', 'Minimum Possible'), ('max', 'Maximum Possible'),
                                                ('range', 'Range')], )

    @api.onchange('indicator_id')
    def _onchange_indicator_id(self):
        if self.indicator_id:
            self.optimal_value = self.indicator_id.optimal_value


class Process(models.Model):
    _name = 'enterprise_mgm_sys.process'

    name = fields.Char(string='Name', required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=False)
    limit = fields.Float(string='Limit', required=True)
    process_file = fields.Many2one(comodel_name='enterprise_mgm_sys.registry', string='Process file', required=False)
    indicator_ids = fields.One2many(comodel_name='enterprise_mgm_sys.process_indicator_line', inverse_name='process_id', string='Indicators')
