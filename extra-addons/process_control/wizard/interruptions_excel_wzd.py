# -*- coding: utf-8 -*-

import json
from odoo import models, fields

class InterruptionsExcelWzd(models.TransientModel):
    _name = 'process_control.interruptions_excel_wzd'
    _description = 'Interruptions excel report wzd'

    start_date = fields.Date('Start Date *', required=True)
    end_date = fields.Date('End Date *', required=True)

    def export_to_xlsx(self):
        data = {
                'start_date': fields.Date.to_string(self.start_date),
                'end_date': fields.Date.to_string(self.end_date),
            }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'report.process_control.interruptions_excel_report',
                     'options': json.dumps(data),
                     'output_format': 'xlsx',
                     'report_name': f'Interruptions Report {self.start_date}-{self.end_date}',
                     },
            'report_type': 'xlsx',
        }
