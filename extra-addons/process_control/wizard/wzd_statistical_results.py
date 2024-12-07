# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdStatisticalResultsToExcel(models.TransientModel):
    _name = 'process_control.statistical_results_to_excel_wzd'

    start_date = fields.Date('Fecha', required=True)
    turn = fields.Many2one(comodel_name="resource.calendar", domain=[('turn_process_control', '=', True)], string="Turno", required=True)


    def export_to_xlsx(self):
        return self.env['report'].get_action(self, 'process_control.statistical_results_report', data={
            'start_date': self.start_date,
            'turn': self.turn.id,

        })

