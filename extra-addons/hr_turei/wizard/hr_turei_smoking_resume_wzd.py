# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class HrTureiSmokingResumeWzd(models.TransientModel):
    _name = 'hr_turei.smoking_resume_wzd'

    def _get_default_connection(self):
        return self.env['db_external_connector.template'].search([('application', '=', 'versat')], limit=1)

    connection_id = fields.Many2one('db_external_connector.template', 'Connection SGP', required=True, default=_get_default_connection)
    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    expedition_date = fields.Date('Expedition Date', required=True, default=fields.Date.context_today)

    def print_report(self):
        return self.env['report'].get_action(self, 'hr_turei.smoking_resume', data={})

