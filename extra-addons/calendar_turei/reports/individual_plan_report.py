# -*- coding: utf-8 -*-
from odoo import models, _

class ReportIndividualPlan(models.AbstractModel):
    _name = 'report.calendar_turei.report_individual_plan'
    _description = 'Report Individual Plan'

    def _get_report_values(self, docids, data=None):
        data = data or {}
        data['day_names'] = [
            _('Mon'), _('Tue'), _('Wed'),
            _('Thu'), _('Fri'), _('Sat'), _('Sun'),
        ]
        return data