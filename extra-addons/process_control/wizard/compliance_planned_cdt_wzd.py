# -*- coding: utf-8 -*-
import json
from odoo import models, fields

class WzdCompliancePlannedCdtToExcel(models.TransientModel):
    _name = 'process_control.compliance_planned_cdt_excel_wzd'
    _description = 'Compliance Planned CDT Report Wzd'

    start_date = fields.Date('Start Date *', required=True)
    end_date = fields.Date('End Date *', required=True)

    def export_to_xlsx(self):
        data = {
                'start_date': fields.Date.to_string(self.start_date),
                'end_date': fields.Date.to_string(self.end_date),
            }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'report.process_control.compliance_planned_cdt',
                     'options': json.dumps(data),
                     'output_format': 'xlsx',
                     'report_name': f'Compliance Planned CDT Excel Report ({self.start_date}-{self.end_date})',
                     },
            'report_type': 'xlsx',
        }
