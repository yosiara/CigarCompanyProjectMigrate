# -*- coding: utf-8 -*-

from odoo import api, tools, _
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.http import addons_manifest


class PlanMttoReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        date = datetime.today().date()
        if lines.year == 'current':
            year = date.year
        else:
            year = date.replace(year=date.year + 1).year

        incident_plan_obj = self.env['maintenance_turei.incident_plan']
        if len(incident_plan_obj.search([('year_char', '=', str(year))])) == 0:
            raise ValidationError(_('Error! No hay incidencias registradas para el: %s') %(year))

        worksheet = workbook.add_worksheet(tools.ustr('PLAN MTTO'))
        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        normal_center_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font': {'size': 11}})

        equipment_obj = self.env['maintenance.equipment']

        domain = [('is_industrial', '=', True), ('state', 'not in', ['fuera_servicio', 'baja'])]

        if lines.category_id:
            domain.append(('category_id', '=', lines.category_id.id))
            # equipment = equipment_obj.search([('category_id', '=', lines.category_id.id), ('is_industrial', '=', True)])
        if lines.maintenance_team_id:
            domain.append(('maintenance_team_id', '=', lines.maintenance_team_id.id))
        # else:
        equipment = equipment_obj.search(domain)

        worksheet.insert_image('A1', addons_manifest['maintenance_turei'][
            'addons_path'] + '/maintenance_turei/static/src/img/tabacuba.jpg',
                               {'x_offset': 15, 'x_scale': 1.8, 'y_scale': 1.8})
        worksheet.merge_range('D2:AB2', tools.ustr("PLAN DE MANTENIMIENTO"), head_format)
        worksheet.merge_range('D3:AB3', tools.ustr("AÑO: %s ") %(year), head_format)
        worksheet.set_column('A5:A5', 3)
        worksheet.write('A5', tools.ustr('No.'), merge_format)
        worksheet.write('B5', tools.ustr('Código'), merge_format)
        worksheet.set_column('C5:C5', 30)
        worksheet.write('C5', tools.ustr('Equipo'), merge_format)
        worksheet.set_column('D5:D5', 10)
        worksheet.write('D5', tools.ustr('Taller'), merge_format)
        worksheet.set_column('E5:AB5', 3)
        worksheet.merge_range('E5:F5', tools.ustr("ENE"), merge_format)
        worksheet.merge_range('G5:H5', tools.ustr("FEB"), merge_format)
        worksheet.merge_range('I5:J5', tools.ustr("MAR"), merge_format)
        worksheet.merge_range('K5:L5', tools.ustr("ABR"), merge_format)
        worksheet.merge_range('M5:N5', tools.ustr("MAY"), merge_format)
        worksheet.merge_range('O5:P5', tools.ustr("JUN"), merge_format)
        worksheet.merge_range('Q5:R5', tools.ustr("JUL"), merge_format)
        worksheet.merge_range('S5:T5', tools.ustr("AGO"), merge_format)
        worksheet.merge_range('U5:V5', tools.ustr("SEP"), merge_format)
        worksheet.merge_range('W5:X5', tools.ustr("OCT"), merge_format)
        worksheet.merge_range('Y5:Z5', tools.ustr("NOV"), merge_format)
        worksheet.merge_range('AA5:AB5', tools.ustr("DIC"), merge_format)

        x = 5
        cont = 1
        dic_pos_meses = {'1': 5, '2': 7, '3': 9, '4': 11, '5': 13, '6': 15,
                         '7': 17, '8': 19, '9': 21, '10': 23, '11': 25, '12': 27}
        dic_semana = {'0': 'Lu', '1': 'Ma', '2': 'Mi', '3': 'Ju', '4': 'Vi', '5': 'Sa', '6': 'Do'}

        for equip in equipment:
            # equip.plan_mtto(year)
            y = x + 1
            worksheet.merge_range(x, 0, y, 0, cont, normal_format)
            worksheet.merge_range(x, 1, y, 1, equip.code, normal_format)
            worksheet.merge_range(x, 2, y, 2, equip.name, normal_format)
            worksheet.merge_range(x, 3, y, 3, equip.category_id.name, normal_format)
            for i in range(4, 28):
                worksheet.write(x, i, "", normal_center_format)
                worksheet.write(y, i, "", normal_center_format)
            for cycle in equip.cycle_maintenance_plan_ids.search([('year_char', '=', str(year)), ('equipment_id', '=', equip.id)]):
                date = datetime.strptime(cycle.date, '%Y-%m-%d').date()
                worksheet.write(x, dic_pos_meses[str(date.month)] - 1, date.isocalendar()[1], normal_center_format)
                worksheet.write(x, dic_pos_meses[str(date.month)], dic_semana[str(date.weekday())], normal_center_format)
                worksheet.write(y, dic_pos_meses[str(date.month)] - 1, cycle.cycle.cycle, normal_center_format)
                worksheet.write(y, dic_pos_meses[str(date.month)], date.day, normal_center_format)
            cont += 1
            x += 2


PlanMttoReport('report.maintenance_turei.plan_mtto_report', 'wzd.plan.mtto')
