# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ContractSingleXlsPercentReport(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri', 'text_wrap': True})
        merge_format1 = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#FFFF33', 'font_color': '#000000', 'font_name': 'Calibri', 'text_wrap': True})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 10}, 'text_wrap': True})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}, 'text_wrap': True})

        worksheet = workbook.add_worksheet(tools.ustr('CONTRATOS'))
        percent = data['percent']
        flow = data['flow']
        domain = []
        if percent:
            domain.append(('percentage_execution', '>=', percent))
        if flow:
            domain.append(('flow', '=', flow))
        contract_ids = self.env['l10n_cu_contract.contract'].search(domain, order='percentage_execution DESC')
        worksheet.merge_range(0, 0, 3, 1, 'FOTO', head_format)
        if flow == 'customer':
            aux = 'ventas'
        else:
            aux = 'compras'
        worksheet.merge_range(0, 2, 3, 9, tools.ustr("Contratos de "+aux+" con un por ciento de ejecución del presupuesto igual o mayor que ") + str(percent), head_format)
        worksheet.set_column('A:A', 2)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 40)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.merge_range(4, 0, 4, 1, tools.ustr('Número'), merge_format)
        worksheet.write('C5', tools.ustr('Empresa'), merge_format)
        worksheet.write('D5', tools.ustr('Denominación'), merge_format)
        worksheet.write('E5', tools.ustr('Fecha Inicio'), merge_format)
        worksheet.write('F5', tools.ustr('Fecha Término'), merge_format)
        worksheet.write('G5', tools.ustr('Total'), merge_format)
        worksheet.write('H5', tools.ustr('Ejecutado'), merge_format)
        worksheet.write('I5', tools.ustr('No Ejecutado'), merge_format)
        worksheet.write('J5', tools.ustr('%'), merge_format)

        x = 5
        for c in contract_ids:
            worksheet.merge_range(x, 0, x, 1,  tools.ustr(c.number), normal_format)
            worksheet.write(x, 2, tools.ustr(c.partner_id.name), normal_format)
            worksheet.write(x, 3, tools.ustr(c.name), normal_format)
            worksheet.write(x, 4, c.date_start, normal_format)
            worksheet.write(x, 5, c.date_end, normal_format)
            worksheet.write(x, 6, '{0:.2f}'.format(c.amount_total).replace('.', ','), normal_format)
            worksheet.write(x, 7, '{0:.2f}'.format(c.amount_invoice).replace('.', ','), normal_format)
            worksheet.write(x, 8, '{0:.2f}'.format(c.amount_rest).replace('.', ','), normal_format)
            worksheet.write(x, 9, '{0:.2f}'.format(c.percentage_execution).replace('.', ','), normal_format)
            x += 1

ContractSingleXlsPercentReport('report.l10n_cu_hlg_contract.contract_single_xls_percent_report.xlsx', 'l10n_cu_contract.to_expire_percent')
