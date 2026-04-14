# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdSummaryTimeFrequencyToExcelTobacco(models.TransientModel):
    _name = 'wzd.summary.time.frequency.to.excel.tobacco'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    turn = fields.Many2one(comodel_name="process_control_tobacco.turno", string="Turno", required=False)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'process_control_tobacco.summary_time_frequency_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'turn': self.turn.id,
        })

