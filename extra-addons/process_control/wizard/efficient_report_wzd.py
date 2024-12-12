# -*- coding: utf-8 -*-


from odoo import models, fields


class WzdEfficientReport(models.TransientModel):
    _name = 'process_control.efficient_report_wzd'

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)
    productive_section = fields.Many2one(comodel_name="process_control.productive_section",
                                         string="Sec. Prod.",
                                         required=False, ondelete='cascade')
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", required=False)

    def print_report(self):
        return self.env['report'].get_action(self, 'process_control.efficient_report', data={
            'start_date': self.start_date,
            'end_date': self.end_date,
            'productive_section': self.productive_section.id,
            'turn': self.turn.id,
        })
