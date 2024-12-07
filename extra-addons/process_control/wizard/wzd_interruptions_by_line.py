# -*- coding: utf-8 -*-


from odoo import models, fields, api


class WzdInterruptionsByLine(models.TransientModel):
    _name = 'process_control.interruptions_line_wzd'

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)
    interruption_type = fields.Many2one('process_control.interruption_type', 'Tipo')
    productive_line = fields.Many2one(comodel_name="process_control.productive_line",
                                         string="Línea productiva", ondelete='cascade')

    def print_report(self):
        return self.env['report'].get_action(self, 'process_control.interruptions_by_line_report', data={
            'start_date': self.start_date,
            'end_date': self.end_date,
            'productive_line': self.productive_line.id,
            'interruption_type': self.interruption_type.id,
        })
