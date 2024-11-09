# -*- coding: utf-8 -*-


from odoo import models, fields, api


class WzdEfficiencyAccomplish(models.TransientModel):
    _name = 'wzd.efficiency.accomplish'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)

    percent = fields.Float('Porciento Efic.', required=True)

    def print_report(self):
        return self.env['report'].get_action(self, 'turei_process_control.efficiency_accomplish_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'percent': self.percent,
        })
