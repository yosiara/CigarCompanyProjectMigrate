# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ContractHiringStatusXlsReport(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri', 'text_wrap': True})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 10}, 'text_wrap': True})
        normal_format_center = workbook.add_format({'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 10}, 'text_wrap': True})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}, 'text_wrap': True})

        worksheet = workbook.add_worksheet(tools.ustr('CONTRATOS DENTRO Y FUERA DEL ORGANISMO'))

        date_end = data['date_end']
        contract_obj = self.env['l10n_cu_contract.contract']

        worksheet.merge_range('A1:B1', tools.ustr("ESTADO DE LA CONTRATACION DENTRO Y FUERA DEL ORGANISMO"), head_format)
        worksheet.merge_range('A2:B2', tools.ustr("FECHA CIERRE: %s") %(date_end), head_format)

        worksheet.set_column('A:A', 50)
        worksheet.set_column('B:B', 20)
        worksheet.write('A3', tools.ustr('TOTAL GENERAL'), normal_format)
        worksheet.write('A4', tools.ustr('Contratos que oferta la empresa'), normal_format)
        worksheet.write('A5', tools.ustr('Contratos que ofertan otras entidades'), normal_format)
        worksheet.write('A6', tools.ustr('Contratos de trabajadores por cuenta propia'), normal_format)
        worksheet.merge_range('A7:B7', tools.ustr(" "), merge_format)
        worksheet.write('A8', tools.ustr('CONTRATOS DENTRO DEL SISTEMA'), normal_format)
        worksheet.write('A9', tools.ustr('Contratos que oferta la empresa'), normal_format)
        worksheet.write('A10', tools.ustr('Contratos que ofertan otras entidades'), normal_format)
        worksheet.merge_range('A11:B11', tools.ustr(" "), merge_format)
        worksheet.write('A12', tools.ustr('CONTRATOS FUERA DEL SISTEMA'), normal_format)
        worksheet.write('A13', tools.ustr('Contratos que oferta la empresa'), normal_format)
        worksheet.write('A14', tools.ustr('Contratos que ofertan otras entidades'), normal_format)
        worksheet.write('A15', tools.ustr('Contratos de trabajadores por cuenta propia'), normal_format)

        total_gral = contract_obj.search_count([('state', '=', 'open'), ('parent_id', '=', False)])
        total_sale = contract_obj.search_count([('state','=', 'open'), ('flow', '=', 'customer'), ('parent_id', '=', False)])
        total_supplier = contract_obj.search_count([('state','=', 'open'), ('flow', '=', 'supplier'), ('parent_id', '=', False)])
        total_gral_ds = contract_obj.search_count([('state','=', 'open'), ('dst', '=', 'si'), ('parent_id', '=', False)])
        total_sale_ds = contract_obj.search_count([('state','=', 'open'), ('flow', '=', 'customer'), ('dst', '=', 'si'), ('parent_id', '=', False)])
        total_supplier_ds = contract_obj.search_count([('state','=', 'open'), ('flow', '=', 'supplier'), ('dst', '=', 'si'), ('parent_id', '=', False)])
        total_gral_fs = contract_obj.search_count([('state','=', 'open'), ('dst', '=', 'no'), ('parent_id', '=', False)])
        total_sale_fs = contract_obj.search_count([('state','=', 'open'), ('flow', '=', 'customer'), ('dst', '=', 'no'), ('parent_id', '=', False)])
        total_supplier_fs = contract_obj.search_count([('state','=', 'open'), ('flow', '=', 'supplier'), ('dst', '=', 'no'), ('parent_id', '=', False)])

        total_tcp = contract_obj.search_count([('state','=', 'open'), ('tcp', '=', 'si'), ('parent_id', '=', False)])
        total_tcp_fs = contract_obj.search_count([('state','=', 'open'), ('tcp', '=', 'si'), ('dst', '=', 'no'), ('parent_id', '=', False)])

        worksheet.write('B3', total_gral + total_tcp_fs, normal_format_center)
        worksheet.write('B4', total_sale, normal_format_center)
        worksheet.write('B5', total_supplier, normal_format_center)
        worksheet.write('B6', total_tcp, normal_format_center)
        worksheet.write('B8', total_gral_ds, normal_format_center)
        worksheet.write('B9', total_sale_ds, normal_format_center)
        worksheet.write('B10', total_supplier_ds, normal_format_center)
        worksheet.write('B12', total_gral_fs + total_tcp_fs, normal_format_center)
        worksheet.write('B13', total_sale_fs, normal_format_center)
        worksheet.write('B14', total_supplier_fs, normal_format_center)
        worksheet.write('B15', total_tcp_fs, normal_format_center)

ContractHiringStatusXlsReport('report.l10n_cu_hlg_contract.contract_hiring_status_xls_report.xlsx', 'l10n_cu_contract.hiring_status')
