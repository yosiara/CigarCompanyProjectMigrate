# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdBDProductionHoursToExcel(models.TransientModel):
    _name = 'process_control.bd_production_hours_excel_wzd'

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)

    def export_to_xlsx(self):
        return self.env['report'].get_action(self, 'process_control.bd_production_hours_report', data={
            'start_date': self.start_date,
            'end_date': self.end_date,
        })

