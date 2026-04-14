# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    tasks_postponed_only = fields.Boolean('Show only postponed tasks', default=False,
                                          help="Show only tasks that change of period in compliance summary")
    chief_signature_on_resume = fields.Boolean('Show chief signature on compliance summary', default=False)
    include_obj_cat_monthly_plan = fields.Boolean('Include objectives and categories in monthly plan', default=False)
    show_jobs_on_plan = fields.Boolean('Show jobs instead names in plans', default=False)
    show_observation_column = fields.Boolean('Show observations column in monthly plans', default=False)
    show_annual_observation_column = fields.Boolean('Show observations column in annual plan', default=False)
    individual_plan_one_week_per_page = fields.Boolean('Show one week per page in individual plan', default=False)
    individual_plan_one_page = fields.Boolean('Show individual plan in one page', default=False)
