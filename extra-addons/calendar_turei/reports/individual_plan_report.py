# -*- coding: utf-8 -*-
##############################################################################
#

from odoo import models

class CalendarReportIndividualPlan(models.TransientModel):
    _name = 'report.calendar_turei.report_individual_plan'
    _description = 'report.calendar_turei.report_individual_plan'

    def _get_report_values(self, docids, data=None):
        docs = data['docs']

        docs = [doc for doc in docs]

        return {
            'docs': docs,
            'report_name': 'report_individual_plan',
            'company': self.env.company,
        }
