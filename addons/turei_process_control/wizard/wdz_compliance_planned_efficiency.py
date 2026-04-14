# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdCompliancePlannedEfficiencyToExcel(models.TransientModel):
    _name = 'wzd.compliance.planned.efficiency.excel'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_process_control.compliance_planned_efficiency', data={
                'date_start': self.date_start,
                'date_end': self.date_end,
            })
