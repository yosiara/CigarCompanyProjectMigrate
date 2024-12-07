# -*- coding: utf-8 -*-

import json
from odoo import models, fields
from odoo.tools import date_utils

class WzdInterruptionsToExcel(models.TransientModel):
    _name = 'process_control.interruptions_to_excel_wzd'
    _description = "Interruptions to excel report wzd"

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)

    def export_to_xlsx(self):
        data = {
                'start_date': self.start_date,
                'end_date': self.end_date,
            }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'report.process_control.interruptions_to_excel_report',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Interruptions Report',
                     },
            'report_type': 'xlsx',
        }
