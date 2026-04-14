# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdSummaryTimeFrequencyToExcel(models.TransientModel):
    _name = 'wzd.summary.time.frequency.to.excel'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", required=False)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'process_control_primary.summary_time_frequency_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'turn': self.turn.id,
        })

