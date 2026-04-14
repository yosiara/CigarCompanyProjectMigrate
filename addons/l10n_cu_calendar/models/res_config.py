# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CalendarConfiguration(models.TransientModel):
    _name = 'calendar.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    tasks_postponed_only = fields.Boolean(related='company_id.tasks_postponed_only', string='Show only postponed tasks',
                                          default=False)
    chief_signature_on_resume = fields.Boolean(related='company_id.chief_signature_on_resume',
                                               string='Show chief signature on compliance summary', default=False)
    include_obj_cat_monthly_plan = fields.Boolean(related='company_id.include_obj_cat_monthly_plan',
                                                  string='Include objectives and categories in monthly plan')
    show_jobs_on_plan = fields.Boolean(related='company_id.show_jobs_on_plan',
                                                  string='Show jobs instead names in plans')
    show_observation_column = fields.Boolean(related='company_id.show_observation_column',
                                                  string='Show observations column in monthly plans')
    show_annual_observation_column = fields.Boolean(related='company_id.show_annual_observation_column',
                                                  string='Show observations column in annual plan')
    individual_plan_one_week_per_page = fields.Boolean(related='company_id.individual_plan_one_week_per_page',
                                                       string='Show one week per page in individual plan')
    individual_plan_one_page = fields.Boolean(related='company_id.individual_plan_one_page',
                                                       string='Show individual plan in one page')
