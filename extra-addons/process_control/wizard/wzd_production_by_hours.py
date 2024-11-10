# -*- coding: utf-8 -*-


from odoo import models, fields, api


class WzdProductionByHours(models.TransientModel):
    _name = 'process_control.production_hours_wzd'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)

    productive_section = fields.Many2one(comodel_name="process_control.productive_section",
                                         string="Sec. Prod.",
                                         required=False, ondelete='cascade')
    turn = fields.Many2one(comodel_name="resource.calendar", domain=[('turn_process_control', '=', True)], string="Turno", required=True)

    def print_report(self):
        return self.env['report'].get_action(self, 'process_control.production_by_hours_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'productive_section': self.productive_section.id,
            'turn': self.turn.id,
        })
