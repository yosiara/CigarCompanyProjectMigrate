# -*- coding: utf-8 -*-


from odoo import models, fields


class WzdProdRegAmf(models.TransientModel):
    _name = 'process_control.prod_reg_amf_report_wzd'

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", domain=[('turn_process_control', '=', True)], required=False)

    def print_report(self):
        return self.env['report'].get_action(self, 'process_control.prod_and_reg_amf_report', data={
            'start_date': self.start_date,
            'end_date': self.end_date,
            'turn': self.turn.id,
        })
