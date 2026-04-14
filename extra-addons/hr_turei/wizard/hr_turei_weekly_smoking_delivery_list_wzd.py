# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class HrTureiWeeklySmokingDeliveryWzd(models.TransientModel):
    _name = 'hr_turei.weekly_smoking_delivery_wzd'

    def _get_default_companies(self):
        return self.env['res.company'].search([('code', '!=', False)])

    def _get_default_connection(self):
        return self.env['db_external_connector.template'].search([('application', '=', 'sgp')], limit=1)

    period_id = fields.Many2one('hr_turei.smoke_period', 'Period', required=True)
    company_ids = fields.Many2one('res.company', 'Company', required=True)
    # company_ids = fields.Many2many('res.company', 'hr_turei_weekly_smoking_wzd_company_rel', 'weekly_smoking_wzd_id', 'company_id', 'Companies', required=True, default=_get_default_companies)
    elaborated_by = fields.Many2one('hr.employee', 'Elaborated by', required=True)
    approved_by = fields.Many2one('hr.employee', 'Approved By', required=True)
    approval = fields.Many2one('hr.employee', 'Approval')
    connection_id = fields.Many2one('db_external_connector.template', 'Connection SGP', required=True, default=_get_default_connection)
    date = fields.Date('Date', required=True, default=fields.Date.context_today)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'hr_turei.weekly_smoking_delivery_list', data={
        })

