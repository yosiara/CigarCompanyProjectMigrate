# -*- coding: utf-8 -*-
import io
import json
import xlsxwriter
from odoo import models, fields, tools
from odoo.tools import date_utils

class TestReportExcel(models.TransientModel):
    _name = 'process_control.test_report'
    
    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)

    def test_report_excel(self):
        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
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
        sheet.merge_range('C4:D4', data["date_start"],txt)
        sheet.merge_range('A5:B5', data["date_end"], cell_format)
        # for i, product in enumerate(data['products'],
        #                             start=5):  # Start at row 6 for products
        #     sheet.merge_range(f'C{i}:D{i}', product, txt)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
