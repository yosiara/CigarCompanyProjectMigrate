# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdResumeTimeFrequencyToExcel(models.TransientModel):
    _name = 'process_control.time_frequency_excel_wzd'

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)
    group_by = fields.Selection(string="Agrupado", selection=[('linea', tools.ustr('Por Línea')), ('seccion', tools.ustr('Por Sesión')), ], required=True, default='seccion')
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", required=False)

    def export_to_xlsx(self):
        if self.group_by == 'seccion':
            return self.env['report'].get_action(self, 'process_control.resume_time_frequency_report', data={
                'start_date': self.start_date,
                'end_date': self.end_date,
                'group_by': self.group_by,
                'turn': self.turn.id,
            })
        return self.env['report'].get_action(self, 'process_control.resume_time_frequency_by_line_report', data={
                'start_date': self.start_date,
                'end_date': self.end_date,
                'group_by': self.group_by,
                'turn': self.turn.id,
            })
