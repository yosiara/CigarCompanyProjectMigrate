# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ContractToExpireXlsReport(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri', 'text_wrap': True})
        merge_format1 = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#FFFF33', 'font_color': '#000000', 'font_name': 'Calibri', 'text_wrap': True})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 10}, 'text_wrap': True})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}, 'text_wrap': True})

        worksheet = workbook.add_worksheet(tools.ustr('CONTRATOS PROXIMOS A VENCER'))

        flow = lines.flow
        domain = [('state', 'in', ['open']),('flow', '=', lines.flow), ('required_parent', '=', False)]

        today = datetime.today().date()
        today = today.replace(day=1)
        date = today + relativedelta(months=1)
        date_end = (date + timedelta(days=-1))
        date1 = today + relativedelta(months=2)
        date_end1 = (date1 + timedelta(days=-1))
        day = ""
        if lines.time == '1':
            domain.append(('date_end', '>=', today.strftime('%Y-%m-%d')))
            domain.append(('date_end', '<=', date_end.strftime('%Y-%m-%d')))
            day = tools.ustr(today.strftime('%d-%m-%Y') + " AL " + date_end.strftime('%d-%m-%Y'))

        elif lines.time == '2':
            date_start = date_end + timedelta(days=1)
            domain.append(('date_end', '>=', date_start.strftime('%Y-%m-%d')))
            domain.append(('date_end', '<=', date_end1.strftime('%Y-%m-%d')))
            day = tools.ustr(date_start.strftime('%d-%m-%Y') + " AL " + date_end1.strftime('%d-%m-%Y'))

        elif lines.time == '3':
            date2 = today + relativedelta(months=3)
            date_end2 = (date2 + timedelta(days=-1))
            date_start1 = date_end1 + timedelta(days=1)
            domain.append(('date_end', '>=', date_start1.strftime('%Y-%m-%d')))
            domain.append(('date_end', '<=', date_end2.strftime('%Y-%m-%d')))
            day = tools.ustr(date_start1.strftime('%d-%m-%Y') + " AL " + date_end2.strftime('%d-%m-%Y'))

        else:
            date2 = today + relativedelta(months=3)
            date_end2 = (date2 + timedelta(days=-1))
            domain.append(('date_end', '>=', today.strftime('%Y-%m-%d')))
            domain.append(('date_end', '<=', date_end2.strftime('%Y-%m-%d')))
            day = tools.ustr(today.strftime('%d-%m-%Y') + " AL " + date_end2.strftime('%d-%m-%Y'))

        contract_ids = self.env['l10n_cu_contract.contract'].search(domain, order='date_end asc')

        worksheet.merge_range('A1:I1', tools.ustr("REGISTRO DE CONTRATO CONTRATOS PROXIMOS A VENCER"), head_format)
        worksheet.merge_range('A2:I2', tools.ustr("PLAZO: %s ") %(tools.ustr(day)), head_format)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 30)
        worksheet.write('A5', tools.ustr('Exp No.'), merge_format)
        worksheet.write('B5', tools.ustr('Número'), merge_format)

        if flow == 'customer':
            worksheet.write('C5', tools.ustr('Cliente'), merge_format)
            worksheet.write('C3', tools.ustr('Contratos de Ventas'), merge_format)
        else:
            worksheet.write('C5', tools.ustr('Proveedor'), merge_format)
            worksheet.write('C3', tools.ustr('Contratos de Compras'), merge_format)
        worksheet.write('D5', tools.ustr('Denominación'), merge_format)
        worksheet.write('E5', tools.ustr('Importe Total'), merge_format)
        worksheet.write('F5', tools.ustr('Fecha Inicio'), merge_format)
        worksheet.write('G5', tools.ustr('Fecha Término'), merge_format)
        worksheet.write('H5', tools.ustr('Días Término'), merge_format)
        worksheet.write('I5', tools.ustr('Especialista'), merge_format)

        x = 5
        for c in contract_ids:
            worksheet.write(x, 0, tools.ustr(c.internal_number_contract if c.internal_number_contract else ""), normal_format)
            worksheet.write(x, 1, tools.ustr(c.number), normal_format)
            worksheet.write(x, 2, tools.ustr(c.partner_id.name), normal_format)
            worksheet.write(x, 3, tools.ustr(c.name), normal_format)
            worksheet.write(x, 4, c.amount_total, normal_format)
            worksheet.write(x, 5, c.date_start, normal_format)
            worksheet.write(x, 6, c.date_end, normal_format)
            date_end = datetime.strptime(c.date_end, '%Y-%m-%d')
            today = datetime.today()
            worksheet.write(x, 7, (date_end - today).days, normal_format)
            worksheet.write(x, 8, tools.ustr(c.related_employee_id.name), normal_format)
            x += 1
        x += 2


ContractToExpireXlsReport('report.l10n_cu_hlg_contract.contract_to_expire_xls_report', 'l10n_cu_contract.to_expire')
