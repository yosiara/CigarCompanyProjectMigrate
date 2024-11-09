# -*- coding: utf-8 -*-


from odoo import models, fields


class WzdEfficientReport(models.TransientModel):
    _name = 'wzd.efficient.report'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    productive_section = fields.Many2one(comodel_name="turei_process_control.productive_section",
                                         string="Sec. Prod.",
                                         required=False, ondelete='cascade')
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", domain=[('turn_process_control', '=', True)], required=False)

    def print_report(self):
        return self.env['report'].get_action(self, 'turei_process_control.efficient_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'productive_section': self.productive_section.id,
            'turn': self.turn.id,
        })
