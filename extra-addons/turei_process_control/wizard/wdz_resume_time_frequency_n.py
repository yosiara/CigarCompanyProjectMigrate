# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdResumeTimeFrequencynToExcel(models.TransientModel):
    _name = 'wzd.resume.time.frequencyn.excel'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    group_by = fields.Selection(string="Agrupado", selection=[('linea', tools.ustr('Por Línea')), ('seccion', tools.ustr('Por Sesión')), ], required=True, default='seccion')
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", domain=[('turn_process_control', '=', True)], required=False)

    def export_to_xls(self):
        if self.group_by == 'seccion':
            return self.env['report'].get_action(self, 'turei_process_control.resume_time_frequencyn_report', data={
                'date_start': self.date_start,
                'date_end': self.date_end,
                'group_by': self.group_by,
                'turn': self.turn.id,
            })
        return self.env['report'].get_action(self, 'turei_process_control.resume_time_frequencyn_by_line_report', data={
                'date_start': self.date_start,
                'date_end': self.date_end,
                'group_by': self.group_by,
                'turn': self.turn.id,
            })
