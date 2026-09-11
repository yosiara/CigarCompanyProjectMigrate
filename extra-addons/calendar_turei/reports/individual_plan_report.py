# -*- coding: utf-8 -*-

from odoo import models

class ReportIndividualPlan(models.TransientModel):
    _name = 'report.calendar_turei.report_individual_plan'
    _description = 'report.calendar_turei.report_individual_plan'

    def _get_report_values(self, docids, data=None):
        return data
