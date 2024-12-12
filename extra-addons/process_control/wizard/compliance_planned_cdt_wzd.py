# -*- coding: utf-8 -*-
import json
from odoo import models, fields
from odoo.tools import date_utils

class WzdCompliancePlannedCdtToExcel(models.TransientModel):
    _name = 'process_control.compliance_planned_cdt_excel_wzd'
    _description = "Compliance Planned CDT Report Wzd"

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)

    def export_to_xlsx(self):
        data = {
                'start_date': self.start_date,
                'end_date': self.end_date,
            }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'report.process_control.compliance_planned_cdt',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Compliance Planned CDT Excel Report',
                     },
            'report_type': 'xlsx',
        }
