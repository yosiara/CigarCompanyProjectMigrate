# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdEfficiencyLtrToExcel(models.TransientModel):
    _name = 'wzd.efficiency.ltr.to.excel'

    date_start = fields.Date('Fecha', required=True)
    turn = fields.Many2one(comodel_name="process_control_tobacco.turno", string="Turno", required=True)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'process_control_tobacco.efficiency_ltr_report', data={
            'date_start': self.date_start,
            'turn': self.turn.id,
        })

