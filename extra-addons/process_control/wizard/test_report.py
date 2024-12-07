# -*- coding: utf-8 -*-
import io
import json
import xlsxwriter
from odoo import models, fields, tools
from odoo.tools import date_utils

class TestReportExcel(models.TransientModel):
    _name = 'process_control.test_report'
    
    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)

    def test_report_excel(self):
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'process_control.test_report',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Process Control Excel Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        print(data)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        sheet.merge_range('B2:I3', 'EXCEL REPORT', head)
        sheet.merge_range('A4:B4', 'Customer:', cell_format)
        sheet.merge_range('C4:D4', data["start_date"],txt)
        sheet.merge_range('A5:B5', data["end_date"], cell_format)
        # for i, product in enumerate(data['products'],
        #                             start=5):  # Start at row 6 for products
        #     sheet.merge_range(f'C{i}:D{i}', product, txt)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
