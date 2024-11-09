# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdStatisticalResultsToExcel(models.TransientModel):
    _name = 'wzd.statistical.results.to.excel'

    date_start = fields.Date('Fecha', required=True)
    turn = fields.Many2one(comodel_name="resource.calendar", domain=[('turn_process_control', '=', True)], string="Turno", required=True)


    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_process_control.statistical_results_report', data={
            'date_start': self.date_start,
            'turn': self.turn.id,

        })

