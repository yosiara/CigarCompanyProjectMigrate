# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdProductionRejectionToExcel(models.TransientModel):
    _name = 'wzd.production.rejection.to.excel'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", domain=[('turn_process_control', '=', True)], required=False)


    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_process_control.production_rejection_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'turn': self.turn.id,

        })

