# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ProductionRejectionToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        if lines.turn:
            tecnolog_control = self.env['turei_process_control.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end),('turn','=', lines.turn.id)])
        else:
            tecnolog_control = self.env['turei_process_control.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)])
        worksheet = workbook.add_worksheet(tools.ustr("Control de Producción y Rechazo"))
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})

        worksheet.merge_range('B2:F2', tools.ustr("Control de Producción y Rechazo "), merge_format)
        worksheet.set_column('B3:B3', 25)
        worksheet.write('B3', tools.ustr('Desde'), normal_format)
        worksheet.set_column('C3:D3', 15)
        worksheet.merge_range('C3:D3', tools.ustr("Hasta"), normal_format)
        worksheet.set_column('E3:F3', 15)
        worksheet.merge_range('E3:F3', tools.ustr("Turno"), normal_format)
        worksheet.write('B4', tools.ustr(lines.date_start), normal_format)
        worksheet.merge_range('C4:D4', tools.ustr(lines.date_end), normal_format)
        if lines.turn:
            worksheet.merge_range('E4:F4', tools.ustr(lines.turn.name[-1:]), normal_format)
        else:
            worksheet.merge_range('E4:F4', tools.ustr("TODOS"), normal_format)
        worksheet.write('B5', tools.ustr(' '), normal_format)
        worksheet.merge_range('C5:F5', tools.ustr("MÁQUINAS"), merge_format)
        worksheet.write('B6', tools.ustr('Indicadores'), merge_format)
        worksheet.set_column('C6:F6', 15)
        worksheet.write('C6', tools.ustr('NANO'), normal_format)
        worksheet.write('D6', tools.ustr('SBO'), normal_format)
        worksheet.write('E6', tools.ustr('SRC'), normal_format)
        worksheet.write('F6', tools.ustr('Total General'), normal_format)
        worksheet.write('B7', tools.ustr('Producción (cajones)'), normal_format)
        worksheet.write('B8', tools.ustr('Rechazo (cajones)'), normal_format)
        worksheet.write('B9', tools.ustr('Índice de Rechazo (%)'), normal_format)

        dic_type= {'NANO':{'produccion':0.00,'rechazo':0.00},'SBO':{'produccion':0.00,'rechazo':0.00},'SRC':{'produccion':0.00,'rechazo':0.00}}

        for tc in tecnolog_control:
            for i in tc.rechazo_nano_sbo_src:
                if i.machine_id.name:
                    if i.machine_id.name.split('-')[0] == 'NANO':
                        dic_type[i.machine_id.name.split('-')[0]]['produccion'] = float(i.produccion_en_cigarrillos)/10000 + dic_type[i.machine_id.name.split('-')[0]]['produccion']
                        dic_type[i.machine_id.name.split('-')[0]]['rechazo'] = float(i.rechazo_en_cigarrillos)/10000 + dic_type[i.machine_id.name.split('-')[0]]['rechazo']
                    else:
                        dic_type[i.machine_id.name.split('-')[0]]['produccion'] = float(i.produccion_en_cajones)/500 + dic_type[i.machine_id.name.split('-')[0]]['produccion']
                        dic_type[i.machine_id.name.split('-')[0]]['rechazo'] = float(i.rechazo_en_cajetillas)/500 + dic_type[i.machine_id.name.split('-')[0]]['rechazo']

        worksheet.write('C7', round(dic_type['NANO']['produccion'],2), normal_format)
        worksheet.write('C8', round(dic_type['NANO']['rechazo'],2), normal_format)
        ind_rech_nano = dic_type['NANO']['rechazo']/(dic_type['NANO']['produccion']+dic_type['NANO']['rechazo'])*100 if (dic_type['NANO']['produccion']+dic_type['NANO']['rechazo'])*100 != 0.0 else 0.0
        worksheet.write('C9', round(ind_rech_nano,2), normal_format)

        worksheet.write('D7', round(dic_type['SBO']['produccion'],2), normal_format)
        worksheet.write('D8', round(dic_type['SBO']['rechazo'],2), normal_format)
        ind_rech_sbo = dic_type['SBO']['rechazo']/(dic_type['SBO']['produccion']+dic_type['SBO']['rechazo'])*100 if (dic_type['SBO']['produccion']+dic_type['SBO']['rechazo'])*100 != 0.0 else 0.0
        worksheet.write('D9', round(ind_rech_sbo,2), normal_format)

        worksheet.write('E7', round(dic_type['SRC']['produccion'],2), normal_format)
        worksheet.write('E8', round(dic_type['SRC']['rechazo'],2), normal_format)
        ind_rech_src = dic_type['SRC']['rechazo']/(dic_type['SRC']['produccion']+dic_type['SRC']['rechazo'])*100 if (dic_type['SRC']['produccion']+dic_type['SRC']['rechazo'])*100 != 0.0 else 0.0
        worksheet.write('E9', round(ind_rech_src,2), normal_format)

        total_prod = dic_type['NANO']['produccion']+dic_type['SBO']['produccion']+dic_type['SRC']['produccion']
        total_rech = dic_type['NANO']['rechazo']+dic_type['SBO']['rechazo']+dic_type['SRC']['rechazo']
        total_ind = ind_rech_nano+ind_rech_sbo+ind_rech_src

        worksheet.write('F7', round(total_prod,2), normal_format)
        worksheet.write('F8', round(total_rech,2), normal_format)
        worksheet.write('F9', round(total_ind,2), normal_format)

ProductionRejectionToExcelReport('report.turei_process_control.production_rejection_report', 'wzd.production.rejection.to.excel')
