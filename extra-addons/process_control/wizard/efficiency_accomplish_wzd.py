# -*- coding: utf-8 -*-


from odoo import models, fields, api


class WzdEfficiencyAccomplish(models.TransientModel):
    _name = 'process_control.efficiency_accomplish_wzd'

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)

    percent = fields.Float('Porciento Efic.', required=True)

    def print_report(self):
        return self.env['report'].get_action(self, 'process_control.efficiency_accomplish_report', data={
            'start_date': self.start_date,
            'end_date': self.end_date,
            'percent': self.percent,
        })
