# -*- coding: utf-8 -*-


from odoo import models, fields


class WzdEfficiencyCdtExcel(models.TransientModel):
    _name = 'process_control.efficiency_cdt_excel_wzd'

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)

    def export_to_xlsx(self):
        return self.env['report'].get_action(self, 'process_control.efficiency_cdt_excel_report', data={
            'start_date': self.start_date,
            'end_date': self.end_date,
        })