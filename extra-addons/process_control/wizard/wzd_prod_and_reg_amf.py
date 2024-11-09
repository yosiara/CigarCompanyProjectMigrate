# -*- coding: utf-8 -*-


from odoo import models, fields


class WzdProdRegAmf(models.TransientModel):
    _name = 'wzd.prod_reg_amf.report'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", domain=[('turn_process_control', '=', True)], required=False)

    def print_report(self):
        return self.env['report'].get_action(self, 'turei_process_control.prod_and_reg_amf_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
            'turn': self.turn.id,
        })
