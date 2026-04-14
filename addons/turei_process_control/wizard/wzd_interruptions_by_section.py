# -*- coding: utf-8 -*-


from odoo import models, fields, api


class WzdInterruptionsBySection(models.TransientModel):
    _name = 'wzd.interruptions.section'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    interruption_type = fields.Many2one('turei_process_control.interruption.type', 'Tipo')
    productive_section = fields.Many2one(comodel_name="turei_process_control.productive_section",
                                         string="Sección productiva", ondelete='cascade')

    def print_report(self):
        return self.env['report'].get_action(self, 'turei_process_control.interruptions_by_section_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'interruption_type': self.interruption_type.id,
            'productive_section': self.productive_section.id,
        })
