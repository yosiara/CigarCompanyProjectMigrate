# -*- coding: utf-8 -*-


from odoo import models, fields


class WzdTimeUseToExcel(models.TransientModel):
    _name = 'process_control.time_use_to_excel_wzd'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'process_control.time_use_to_excel_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
        })
