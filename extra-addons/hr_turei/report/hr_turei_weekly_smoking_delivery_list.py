# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, relativedelta
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

HR_TUREI_KEYS_ABSENTEEISM = ['CMD', 'AA', 'AI', 'LS', '49', 'M10', 'Inv', 'TB', 'TA', '048', '12', '31', '32', '35',
                             '37', '42', 'CAR', 'CCO', 'CU', 'DIS', 'ESC', 'IMP', 'INR', 'ISG', 'MIC', 'MOV', 'ORG',
                             'S7', 'U', 'LMT', 'RSM', 'AC']


class HrTureiWeeklySmokingDeliveryList(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format.set_text_wrap()
        merge_format_no_border = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format_no_border.set_text_wrap()
        merge_format_border_right = workbook.add_format(
            {'bold': 0, 'right': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format_border_right.set_text_wrap()
        merge_format_normal = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format_normal.set_text_wrap()
        merge_format_vtop = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'top', 'font_size': 10})
        merge_format_vtop.set_text_wrap()
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 10})
        normal_format.set_text_wrap()
        normal_center_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        normal_center_format.set_text_wrap()
        sign_format = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vdistributed', 'font_size': 10})
        sign_format.set_text_wrap()
        sign_format.set_indent(4)
        identification_format = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vcenter', 'font_size': 8})

        ueb_list = []
        page = 1
        for company in lines.company_ids:
            worksheet = self.set_up_worksheet(workbook, str(page), lines, merge_format_no_border, identification_format, merge_format_normal)
            page += 1
            departments = self.env['hr.department'].search([('company_id', '=', company.id)])
            start_date = fields.Datetime.from_string(lines.period_id.start_date)
            end_date = fields.Datetime.from_string(lines.period_id.end_date)
            start_date_production = fields.Datetime.from_string(lines.period_id.start_date_production)
            end_date_production = fields.Datetime.from_string(lines.period_id.end_date_production)
            turns = lines.period_id.resource_calendar_ids.ids
            department_list = []
            dict_calculations = {'rrhh': {}, 'ptrc': {}, 'hebra': {}}

            connection = lines.connection_id.connect()
            cursor = connection.cursor()

            employees_checked_to_insert = {}
            for department in departments:
                department_dict = {}

                for concept in self.env['hr_turei.cigarette_concept'].search([('department_ids', 'in', department.id)]):
                    if concept.delivery_frequency != 'per_month' or lines.period_id.include_monthly_concepts:
                        if department.is_productive:
                            start_date_aux = start_date_production
                            end_date_aux = end_date_production
                        else:
                            start_date_aux = start_date
                            end_date_aux = end_date

                        if concept.type == 'to_insert':
                            if concept.id not in employees_checked_to_insert:
                                employees_checked_to_insert[concept.id] = {}
                            while start_date_aux <= end_date_aux:
                                ids = self._get_template_department(department.id, start_date_aux)
                                for employee in self.env['hr.employee'].search([('id', 'in', ids)]):
                                    if employee.calendar_id.id in turns and employee.id not in \
                                            employees_checked_to_insert[concept.id]:
                                        register_add_incidences = self.env['hr_turei.additional_incidences'].search(
                                            [('employee_id', '=', employee.id),
                                             ('period_id', '=', lines.period_id.id)], limit=1)
                                        for incidence in register_add_incidences.line_ids:
                                            if incidence.concept_id.id == concept.id:
                                                self._init_department_dict(department_dict, employee, concept)
                                                department_dict[employee.id]['concepts'][concept.id][
                                                    'packs'] = incidence.packs
                                                if incidence.hours_amount > 0.00:
                                                    department_dict[employee.id]['concepts'][concept.id]['name'] = str(
                                                        int(incidence.hours_amount)) + ' ' + concept.name
                                                employees_checked_to_insert[concept.id][employee.id] = True
                                start_date_aux = start_date_aux + relativedelta(days=1)
                        else:

                            while start_date_aux <= end_date_aux:

                                ids = self._get_template_department(department.id, start_date_aux)
                                for employee in self.env['hr.employee'].search([('id', 'in', ids)]):
                                    if employee.calendar_id.id in turns:
                                        working_hours = self._working_hours(employee.calendar_id, start_date_aux)
                                        if working_hours > 0.0:

                                            if concept.type == 'normal':
                                                incidences = self.env['hr_turei.attendance_incidence'].search(
                                                    [('employee_id', '=', employee.id), ('date', '=', start_date_aux),
                                                     ('working_time', '<=', 0.0),
                                                     ('reason_code', 'in', HR_TUREI_KEYS_ABSENTEEISM)])
                                                if not len(incidences):
                                                    self._init_department_dict(department_dict, employee, concept)
                                                    department_dict[employee.id]['concepts'][concept.id][
                                                        'hours'] += working_hours

                                            if concept.type == 'incentive':
                                                incidences = self.env['hr_turei.attendance_incidence'].search(
                                                    [('employee_id', '=', employee.id), ('date', '=', start_date_aux),
                                                     ('working_time', '<=', 0.0)])
                                                if not len(incidences):
                                                    turn_id = employee.calendar_id.sgp_turn_id.sgp_id
                                                    module_id = False
                                                    if employee.smoking_prod_incentive_plan_type == 'rrhh':
                                                        if employee.smoking_prod_incentive_context == 'module':
                                                            transitory_movement = self.env[
                                                                'hr_turei.employee_movement'].search(
                                                                [('employee_id', '=', employee.id),
                                                                 ('movement_type', '=', 'TR'), '|', '&',
                                                                 ('movement_start_date', '<=', start_date_aux),
                                                                 ('movement_end_date', '>=', start_date_aux), '&',
                                                                 ('movement_start_date', '<=', start_date_aux),
                                                                 ('movement_end_date', '=', False)],
                                                                order='movement_start_date desc',
                                                                limit=1)
                                                            if transitory_movement:
                                                                sgp_module = self.env[
                                                                    'hr_sgp_integration.module'].search([(
                                                                    'department_ids',
                                                                    'in',
                                                                    transitory_movement.new_job_position_id.department_id.id)])
                                                                module_id = sgp_module.sgp_id
                                                            else:
                                                                sgp_module = self.env[
                                                                    'hr_sgp_integration.module'].search([(
                                                                    'department_ids',
                                                                    'in',
                                                                    department.id)])
                                                                module_id = sgp_module.sgp_id

                                                            if turn_id and module_id and self._check_production_overcompliance(
                                                                    dict_calculations, cursor, concept, start_date_aux,
                                                                    employee.smoking_prod_incentive_reject, turn_id,
                                                                    module_id):
                                                                self._init_department_dict(department_dict, employee,
                                                                                           concept)
                                                                department_dict[employee.id]['concepts'][concept.id][
                                                                    'hours'] += working_hours

                                                        elif employee.smoking_prod_incentive_context == 'turn':
                                                            if turn_id and self._check_production_overcompliance(
                                                                    dict_calculations, cursor, concept, start_date_aux,
                                                                    turn_id):
                                                                self._init_department_dict(department_dict, employee,
                                                                                           concept)
                                                                department_dict[employee.id]['concepts'][concept.id][
                                                                    'hours'] += working_hours
                                                        elif employee.smoking_prod_incentive_context == 'ueb':
                                                            if self._check_production_overcompliance(
                                                                    dict_calculations, cursor, concept, start_date_aux):
                                                                self._init_department_dict(department_dict, employee,
                                                                                           concept)
                                                                department_dict[employee.id]['concepts'][concept.id][
                                                                    'hours'] += working_hours

                                                    elif employee.smoking_prod_incentive_plan_type == 'ptrc':
                                                        if self._check_ptrc_production_overcompliance(
                                                                dict_calculations, cursor, concept, start_date_aux):
                                                            self._init_department_dict(department_dict, employee,
                                                                                       concept)
                                                            department_dict[employee.id]['concepts'][concept.id][
                                                                'hours'] += working_hours
                                                    elif employee.smoking_prod_incentive_plan_type == 'hebra':
                                                        if employee.smoking_prod_incentive_context == 'turn':
                                                            if turn_id and self._check_hebra_production_overcompliance(
                                                                    dict_calculations, cursor, concept, start_date_aux,
                                                                    turn_id):
                                                                self._init_department_dict(department_dict, employee,
                                                                                           concept)
                                                                department_dict[employee.id]['concepts'][concept.id][
                                                                    'hours'] += working_hours
                                                        elif employee.smoking_prod_incentive_context == 'ueb':
                                                            if self._check_hebra_production_overcompliance(
                                                                    dict_calculations, cursor, concept, start_date_aux):
                                                                self._init_department_dict(department_dict, employee,
                                                                                           concept)
                                                                department_dict[employee.id]['concepts'][concept.id][
                                                                    'hours'] += working_hours

                                start_date_aux = start_date_aux + relativedelta(days=1)

                if len(department_dict):
                    department_list.append({'name': department.name, 'employees': department_dict})

            cursor.close()
            connection.close()

            i = 5
            total = 0
            page_total = 0
            added_lines = 0
            for department in department_list:
                row_start_department = i
                total_department = 0
                j = 0
                for employee_id in department['employees']:
                    if added_lines + len(department['employees'][employee_id]['concepts']) + 1 >= 44:
                        added_lines = 0
                        if i > row_start_department:
                            worksheet.merge_range(row_start_department, 1, i - 1, 1, department['name'],
                                                  merge_format_vtop)
                        self.close_worksheet(worksheet, company.name, i, page_total, lines, merge_format_vtop, merge_format, sign_format)
                        worksheet = self.set_up_worksheet(workbook, str(page), lines, merge_format_no_border, identification_format, merge_format_normal)
                        page += 1
                        page_total = 0
                        row_start_department = i = 5

                    total_employee = 0
                    row_start_employee = i
                    for concept_id in department['employees'][employee_id]['concepts']:
                        if department['employees'][employee_id]['concepts'][concept_id]['type'] == 'per_month':
                            worksheet.write(i, 5, department['employees'][employee_id]['concepts'][concept_id]['packs'],
                                            merge_format_vtop)
                            worksheet.write(i, 4, department['employees'][employee_id]['concepts'][concept_id]['name'],
                                            merge_format_vtop)
                            total_employee += department['employees'][employee_id]['concepts'][concept_id]['packs']
                        elif department['employees'][employee_id]['concepts'][concept_id]['type'] == 'per_day':
                            days = round(float(department['employees'][employee_id]['concepts'][concept_id]['hours'] /
                                               department['employees'][employee_id]['concepts'][concept_id][
                                                   'hours_perday']))
                            packs = days * department['employees'][employee_id]['concepts'][concept_id][
                                'packs_per_unity']
                            worksheet.write(i, 5, packs, merge_format_vtop)
                            worksheet.write(i, 4, '%s %s' % (
                                str(int(days)), department['employees'][employee_id]['concepts'][concept_id]['name']),
                                            merge_format_vtop)
                            total_employee += packs
                        elif department['employees'][employee_id]['concepts'][concept_id]['type'] == 'per_hour':
                            packs = round(department['employees'][employee_id]['concepts'][concept_id]['hours'] *
                                          department['employees'][employee_id]['concepts'][concept_id][
                                              'packs_per_unity'])
                            worksheet.write(i, 5, packs, merge_format_vtop)
                            worksheet.write(i, 4, '%s %s' % (
                                str(int(department['employees'][employee_id]['concepts'][concept_id]['hours'])),
                                department['employees'][employee_id]['concepts'][concept_id]['name']),
                                            merge_format_vtop)
                            total_employee += packs
                        i += 1
                        added_lines += 1
                    if i > row_start_employee:
                        if i - 1 > row_start_employee:
                            worksheet.merge_range(row_start_employee, 3, i - 1, 3,
                                                  department['employees'][employee_id]['name'], merge_format_vtop)
                        else:
                            worksheet.write(row_start_employee, 3, department['employees'][employee_id]['name'],
                                            merge_format_vtop)

                        worksheet.merge_range(row_start_employee, 6, i, 6, tools.ustr(''), merge_format_vtop)
                        worksheet.merge_range(row_start_employee, 2, i, 2, department['employees'][employee_id]['code'],
                                              merge_format_vtop)
                        worksheet.merge_range(i, 3, i, 4, 'Total %s' % department['employees'][employee_id]['name'],
                                              merge_format_vtop)
                        worksheet.write(i, 5, total_employee, merge_format_vtop)
                        total_department += total_employee
                        page_total += total_employee
                        i += 1
                        added_lines += 1

                    j += 1

                if i > row_start_department:
                    total += total_department
                    worksheet.merge_range(row_start_department, 1, i - 1, 1, department['name'], merge_format_vtop)
                    # worksheet.merge_range(i, 1, i, 4, 'Total %s' % department['name'], merge_format)
                    # worksheet.write(i, 5, total_department, merge_format_vtop)
                    # worksheet.write(i, 6, tools.ustr(''), merge_format_vtop)
                    # i += 1
                    # added_lines += 1

            for area in self.env['hr_turei.external_area'].search([('company_id', '=', company.id)]):
                row_start_area = i
                total_area = 0
                if area.weekly_list_delivery_type != 'monthly' or lines.period_id.include_monthly_areas:
                    for person in area.external_staff_ids:
                        concepts = []
                        total_person = 0

                        register_add_incidences = self.env['hr_turei.additional_incidences'].search(
                            [('external_staff_id', '=', person.id),
                             ('period_id', '=', lines.period_id.id), ('employee', '=', False)], limit=1)
                        for incidence in register_add_incidences.line_ids:
                            total_person += incidence.packs
                            name = incidence.concept_id.name
                            if incidence.hours_amount > 0.00:
                                name = str(int(incidence.hours_amount)) + ' ' + incidence.concept_id.name

                            concepts.append({'name': name, 'packs': incidence.packs})

                        days = 0
                        packs = 0
                        concept_name = ''
                        if area.weekly_list_delivery_type == 'daily':
                            attendance_line = self.env['hr_turei.external_staff_attendance.line'].search(
                                [('external_staff_id', '=', person.id),
                                 ('attendance_id.external_area_id', '=', area.id),
                                 ('attendance_id.period_id', '=', lines.period_id.id)], limit=1)
                            if attendance_line:
                                days = attendance_line.days
                                packs = days * area.weekly_list_delivery_concept.packs_amount
                                concept_name = '%s %s' % (str(days), area.weekly_list_delivery_concept.name)
                        elif area.weekly_list_delivery_type == 'weekly':
                            packs = area.weekly_list_delivery_concept.packs_amount
                            concept_name = area.weekly_list_delivery_concept.name
                        elif area.weekly_list_delivery_type == 'monthly' and lines.period_id.include_monthly_areas:
                            packs = area.weekly_list_delivery_concept.packs_amount
                            concept_name = area.weekly_list_delivery_concept.name

                        if packs and concept_name != '':
                            total_person += packs
                            concepts.append({'name': tools.ustr(concept_name), 'packs': packs})

                        if len(concepts) and added_lines + len(concepts) + 1 >= 44:
                            added_lines = 0
                            worksheet.merge_range(row_start_area, 1, i - 1, 1, area['name'], merge_format_vtop)
                            self.close_worksheet(worksheet, company.name, i, page_total, lines, merge_format_vtop,
                                                 merge_format, sign_format)
                            worksheet = self.set_up_worksheet(workbook, str(page), lines, merge_format_no_border,
                                                              identification_format, merge_format_normal)
                            page += 1
                            page_total = 0
                            row_start_area = i = 5

                        row_start_person = i
                        for concept in concepts:
                            worksheet.write(i, 5, concept['packs'], merge_format_vtop)
                            worksheet.write(i, 4, concept['name'], merge_format_vtop)
                            i += 1
                            added_lines += 1

                        if total_person > 0:
                            if i - 1 > row_start_person:
                                worksheet.merge_range(row_start_person, 3, i - 1, 3, person.name, merge_format_vtop)
                            else:
                                worksheet.write(row_start_person, 3, person.name, merge_format_vtop)
                            worksheet.merge_range(row_start_person, 6, i, 6, tools.ustr(''), merge_format_vtop)
                            worksheet.merge_range(row_start_person, 2, i, 2, person.code if person.code else '',
                                                  merge_format_vtop)
                            worksheet.merge_range(i, 3, i, 4, 'Total %s' % person.name, merge_format_vtop)
                            worksheet.write(i, 5, total_person, merge_format_vtop)
                            i += 1
                            added_lines += 1

                        total_area += total_person
                        page_total += total_person

                if i > row_start_area:
                    total += total_area
                    worksheet.merge_range(row_start_area, 1, i - 1, 1, area.name, merge_format_vtop)
                    # worksheet.merge_range(i, 1, i, 4, 'Total %s' % area.name, merge_format)
                    # worksheet.write(i, 5, total_area, merge_format_vtop)
                    # worksheet.write(i, 6, tools.ustr(''), merge_format_vtop)
                    # i += 1
                    # added_lines += 1

            if added_lines:
                self.close_worksheet(worksheet, company.name, i, page_total, lines, merge_format_vtop, merge_format,
                                     sign_format)

            ueb_list.append({'name': company.name, 'total': total})



        if len(ueb_list):
            merge_cover_page_title = workbook.add_format(
                {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
            merge_cover_page_title.set_text_wrap()
            merge_cover_page_enterprise_name = workbook.add_format(
                {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 18})
            merge_cover_page_enterprise_name.set_text_wrap()
            merge_cover_page_date = workbook.add_format(
                {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 16})
            merge_cover_page_date.set_text_wrap()
            merge_cover_page_report_title = workbook.add_format(
                {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 14})
            merge_cover_page_report_title.set_text_wrap()
            merge_cover_page_table = workbook.add_format(
                {'bold': 1, 'border': 1, 'border_color': '#663300', 'align': 'center', 'valign': 'vcenter',
                 'font_size': 14})
            merge_cover_page_table.set_text_wrap()
            merge_cover_page_area = workbook.add_format(
                {'bold': 0, 'border': 1, 'border_color': '#663300', 'align': 'left', 'valign': 'vcenter',
                 'font_size': 14})
            merge_cover_page_area.set_text_wrap()
            cover_page_identification_format = workbook.add_format(
                {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vcenter', 'font_size': 9})
            cover_page_identification_format.set_indent(5)
            sign_format_cover_page = workbook.add_format(
                {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vdistributed', 'font_size': 10})
            sign_format_cover_page.set_text_wrap()

            worksheet = workbook.add_worksheet(tools.ustr('Resumen Empresa'))
            worksheet.set_landscape()
            worksheet.insert_image('A1', addons_manifest['hr_turei'][
                'addons_path'] + '/hr_turei/static/src/img/logo-landscape.jpg',
                                   {'x_offset': 2, 'y_offset': 2, 'x_scale': 1, 'y_scale': 1.5})
            worksheet.merge_range('C1:E3',
                                  tools.ustr(
                                      'INFORME DE ASISTENCIA FÍSICA DE TRABAJADORES POR ÁREAS DE RESPONSABILIDAD'),
                                  merge_cover_page_title)
            list_date = fields.Date.from_string(lines.date)
            worksheet.merge_range('A1:B3', tools.ustr(''), cover_page_identification_format)
            worksheet.merge_range('F1:G1', tools.ustr('Versión: 00'), cover_page_identification_format)
            worksheet.merge_range('F2:G2', tools.ustr('Fecha: 01/08/2018'), cover_page_identification_format)
            worksheet.merge_range('F3:G3', tools.ustr('PE-DCH-02-R-04'), cover_page_identification_format)

            worksheet.merge_range('C7:E8',
                                  tools.ustr(
                                      'EMPRESA DE CIGARROS "LÁZARO PEÑA"'),
                                  merge_cover_page_enterprise_name)

            worksheet.merge_range('C10:E10',
                                  tools.ustr('%s de %s de %s' % (list_date.day, self._get_month_string(list_date.month),
                                                                 list_date.year)), merge_cover_page_date)

            worksheet.merge_range('B12:F12', tools.ustr('CUADRE DE CAJETILLAS A TRASLADAR A LA CASA DE VENTAS'),
                                  merge_cover_page_report_title)

            worksheet.set_column('A1:A1', 15)
            worksheet.set_column('B1:B1', 14)
            worksheet.set_column('C1:C1', 8)
            worksheet.set_column('D1:D1', 40)
            worksheet.set_column('E1:E1', 12)
            worksheet.set_column('F1:F1', 14)
            worksheet.set_column('G1:G1', 8)
            worksheet.set_row(6, 30)
            worksheet.set_row(7, 30)
            worksheet.set_margins(0.3, 0.3, 0.3, 0.3)
            worksheet.fit_to_pages(1, 0)

            worksheet.merge_range('C15:D15', tools.ustr('Áreas'), merge_cover_page_table)
            worksheet.write('E15', tools.ustr('Cantidad'), merge_cover_page_table)

            i = 15
            total = 0
            for company in ueb_list:
                worksheet.merge_range(i, 2, i, 3, tools.ustr(company['name']), merge_cover_page_area)
                worksheet.write(i, 4, int(company['total']), merge_cover_page_table)
                total += company['total']
                i += 1

            worksheet.merge_range(i, 2, i, 3, tools.ustr('Total'), merge_cover_page_table)
            worksheet.write(i, 4, int(total), merge_cover_page_table)

            worksheet.merge_range('A26:C26', tools.ustr(
                'Elaborado por: %s' % lines.elaborated_by.name if lines.elaborated_by else ''), sign_format_cover_page)
            worksheet.merge_range('A27:C27', tools.ustr(
                'Cargo: %s' % lines.elaborated_by.job_id.name if lines.elaborated_by else ''), sign_format_cover_page)
            worksheet.merge_range('A28:C28', tools.ustr('Firma: _______'), sign_format_cover_page)

            worksheet.write('D26', tools.ustr('Aprobado por: %s' % lines.approved_by.name if lines.approved_by else ''),
                            sign_format_cover_page)
            worksheet.write('D27', tools.ustr('Cargo: %s' % lines.approved_by.job_id.name if lines.approved_by else ''),
                            sign_format_cover_page)
            worksheet.write('D28', tools.ustr('Firma: _______'), sign_format_cover_page)

            worksheet.merge_range('E26:G26',
                                  tools.ustr('Visto Bueno: %s' % lines.approval.name if lines.approval else ''),
                                  sign_format_cover_page)
            worksheet.merge_range('E27:G27',
                                  tools.ustr('Cargo: %s' % lines.approval.job_id.name if lines.approval else ''),
                                  sign_format_cover_page)
            worksheet.merge_range('E28:G28', tools.ustr('Firma: _______'), sign_format_cover_page)

    def close_worksheet(self, worksheet, name, i, total, lines, merge_format_vtop, merge_format,sign_format):

        if i > 5:
            worksheet.merge_range(5, 0, i - 1, 0, name, merge_format_vtop)
            worksheet.merge_range(i, 0, i, 4, 'Total %s' % name, merge_format)
            worksheet.write(i, 5, total, merge_format_vtop)
            worksheet.write(i, 6, tools.ustr(''), merge_format_vtop)
            i += 1

        worksheet.merge_range(i + 2, 0, i + 2, 2, 'Elaborado por: %s' % tools.ustr(lines.elaborated_by.name),
                              sign_format)
        worksheet.merge_range(i + 3, 0, i + 3, 2, 'Cargo: %s' % tools.ustr(lines.elaborated_by.job_id.name),
                              sign_format)
        worksheet.merge_range(i + 4, 0, i + 4, 2, 'Firma: _________', sign_format)
        worksheet.merge_range(i + 2, 4, i + 2, 6, 'Aprobado por: %s' % tools.ustr(lines.approved_by.name),
                              sign_format)
        worksheet.merge_range(i + 3, 4, i + 3, 6, 'Cargo: %s' % tools.ustr(lines.approved_by.job_id.name),
                              sign_format)
        worksheet.merge_range(i + 4, 4, i + 4, 6, 'Firma: _________', sign_format)

        return worksheet

    def set_up_worksheet(self, workbook, name, lines, merge_format_no_border, identification_format, merge_format_normal):
        worksheet = workbook.add_worksheet(tools.ustr(name))
        worksheet.insert_image('A1', addons_manifest['hr_turei'][
            'addons_path'] + '/hr_turei/static/src/img/logo-landscape.jpg',
                               {'x_offset': 2, 'y_offset': 2, 'x_scale': 0.6, 'y_scale': 1})
        worksheet.merge_range('B1:F2',
                              tools.ustr(
                                  'INFORME DE ASISTENCIA FÍSICA DE TRABAJADORES POR ÁREAS DE RESPONSABILIDAD'),
                              merge_format_no_border)
        list_date = fields.Date.from_string(lines.date)
        worksheet.merge_range('B3:F3', tools.ustr('Correspondiente al %s: %s de %s de %s' % (
            self._get_day_string(list_date.weekday()), list_date.day, self._get_month_string(list_date.month),
            list_date.year)), merge_format_no_border)
        worksheet.merge_range('A1:A3', tools.ustr(''), merge_format_no_border)
        worksheet.write('G1', tools.ustr('Versión: 00'), identification_format)
        worksheet.write('G2', tools.ustr('Fecha: 01/08/2018'), identification_format)
        worksheet.write('G3', tools.ustr('PE-DCH-02-R-02'), identification_format)
        worksheet.write('A5', tools.ustr('UEB'), merge_format_normal)
        worksheet.write('B5', tools.ustr('Área'), merge_format_normal)
        worksheet.write('C5', tools.ustr('Código'), merge_format_normal)
        worksheet.write('D5', tools.ustr('Nombre y Apellidos'), merge_format_normal)
        worksheet.write('E5', tools.ustr('Concepto'), merge_format_normal)
        worksheet.write('F5', tools.ustr('Cajetillas'), merge_format_normal)
        worksheet.write('G5', tools.ustr('Firma'), merge_format_normal)

        worksheet.set_column('A1:A1', 12)
        worksheet.set_column('B1:B1', 17)
        worksheet.set_column('C1:C1', 7)
        worksheet.set_column('D1:D1', 25)
        worksheet.set_column('E1:E1', 23)
        worksheet.set_column('F1:F1', 7)
        worksheet.set_column('G1:G1', 13)
        worksheet.repeat_rows(0, 4)
        worksheet.set_margins(0.3, 0.3, 0.3, 0.3)
        worksheet.fit_to_pages(1, 0)

        return worksheet

    def _init_department_dict(self, department_dict, employee, concept):
        if employee.id not in department_dict:
            department_dict[employee.id] = {'name': employee.name, 'code': employee.code,
                                            'concepts': {}}

        if concept.id not in department_dict[employee.id]['concepts']:
            department_dict[employee.id]['concepts'][concept.id] = {'name': concept.name,
                                                                    'packs_per_unity': concept.packs_amount,
                                                                    'type': concept.delivery_frequency, 'packs': 0,
                                                                    'hours': 0, 'hours_perday': concept.hours_perday}

    def _working_hours(self, calendar, date):
        if calendar:
            return calendar.get_working_hours_of_date(date)

    def _get_template_department(self, department_id, start_date_aux):
        ids = self.env['hr_turei.employee_movement'].read_group(
            domain=[('new_job_position_id.department_id', '=', department_id), '|',
                    ('movement_type', 'in', ['R', 'PR']),
                    '|', '&',
                    ('movement_start_date', '<=', start_date_aux),
                    ('movement_end_date', '>=', start_date_aux), '&',
                    ('movement_start_date', '<=', start_date_aux), ('movement_end_date', '=', False)],
            fields=['employee_id'], groupby=['employee_id'])
        ids = map(lambda x: x['employee_id'][0], ids)
        return ids

    def _check_production_overcompliance(self, dict_calculations, cursor, concept, date, rejection=False, turn_id=False,
                                         module_id=False):

        date_string = fields.Date.to_string(date)
        calculated = False
        porciento_cumplimiento = 0.0
        accomplish_rejection = False

        if date_string in dict_calculations['rrhh']:
            if turn_id and not module_id and turn_id in dict_calculations['rrhh'][date_string]:
                porciento_cumplimiento = dict_calculations['rrhh'][date_string][turn_id]['val']
                accomplish_rejection = dict_calculations['rrhh'][date_string][turn_id]['accomplish_rejection']
                calculated = True
            if turn_id and module_id and (str(turn_id) + '-' + str(module_id)) in dict_calculations['rrhh'][
                date_string]:
                porciento_cumplimiento = dict_calculations['rrhh'][date_string][(str(turn_id) + '-' + str(module_id))][
                    'val']
                accomplish_rejection = dict_calculations['rrhh'][date_string][(str(turn_id) + '-' + str(module_id))][
                    'accomplish_rejection']
                calculated = True
            elif not turn_id and not module_id and 'ueb' in dict_calculations['rrhh'][date_string]:
                porciento_cumplimiento = dict_calculations['rrhh'][date_string]['ueb']['val']
                accomplish_rejection = dict_calculations['rrhh'][date_string]['ueb']['accomplish_rejection']
                calculated = True
        else:
            dict_calculations['rrhh'][date_string] = {}

        if not calculated:
            params = [date]
            query_plan = u"""SELECT
                    Sum("public".pt_plan_rrhh_distribucion.plan)
                    FROM
                    "public".pt_plan_rrhh_distribucion
                    WHERE
                    "public".pt_plan_rrhh_distribucion.fecha = '%s'"""

            query_production = u"""SELECT
                    CASE WHEN (Sum("public".pt_produccion_terminada.cantidad_producida)) IS NULL THEN
                    (0) ELSE (Sum("public".pt_produccion_terminada.cantidad_producida)) END AS prod
                    FROM
                    "public".pt_produccion_terminada
                    WHERE
                    "public".pt_produccion_terminada.fecha = '%s'"""

            if turn_id and not module_id:
                query_farol = u"""SELECT
                        Sum("public".nc_desecho.cantidad_desechos) AS farol,
                        Sum("public".nc_desecho.plan)/10 AS plan
                        FROM
                        "public".nc_desecho
                        INNER JOIN "public".cd_desecho_marca ON "public".nc_desecho.id_desecho_marca = "public".cd_desecho_marca."id"
                        WHERE
                        "public".nc_desecho.fecha = '%s' AND                         
                        "public".nc_desecho.id_taller = %s AND
                        "public".cd_desecho_marca.id_desecho IN (5, 6)
                        """
            else:
                query_farol = u"""SELECT Sum("public".nc_desecho.cantidad_desechos) AS farol,
                                        "public".nc_desecho.plan
                                        FROM
                                        "public".nc_desecho
                                        INNER JOIN "public".cd_desecho_marca ON "public".nc_desecho.id_desecho_marca = "public".cd_desecho_marca."id"
                                        INNER JOIN "public".cd_brigada_modulo ON "public".nc_desecho.id_brigada_modulo = "public".cd_brigada_modulo."id"
                                        WHERE
                                        "public".nc_desecho.fecha = '%s' AND
                                        "public".nc_desecho.id_taller = %s AND
                                        "public".cd_desecho_marca.id_desecho IN (5, 6) AND
                                        "public".cd_brigada_modulo.id_modulo = %s
                                        GROUP BY
                                       "public".nc_desecho.plan"""

            query_farol_plan = u"""SELECT
                        "public".cd_variable_valor.id_variable,
                        "public".cd_variable_valor.fecha,
                        "public".cd_variable_valor.valor,
                        "public".cd_variable_valor."id"
                        FROM
                        "public".cd_variable_valor
                        WHERE
                        "public".cd_variable_valor.id_variable = %s AND
                        "public".cd_variable_valor.fecha <= '%s'
                        ORDER BY
                        "public".cd_variable_valor."id" DESC
                        LIMIT 1"""

            query_rechazos = u"""SELECT
                                Sum("public".nc_rechazos_cajones.cant_rechazos)
                                FROM
                                "public".nc_rechazos_cajones
                                WHERE
                                "public".nc_rechazos_cajones.fecha = '%s'"""

            query_rechazos_plan = u"""SELECT
                                "public".cd_variable_valor.id_variable,
                                "public".cd_variable_valor.fecha,
                                "public".cd_variable_valor.valor,
                                "public".cd_variable_valor."id"
                                FROM
                                "public".cd_variable_valor
                                WHERE
                                "public".cd_variable_valor.id_variable = %s AND
                                "public".cd_variable_valor.fecha <= '%s'
                                ORDER BY
                                "public".cd_variable_valor."id" DESC
                                LIMIT 1"""

            if turn_id:
                params.append(turn_id)
                var_farol_plan = 41
                var_rechazos_plan = 39
                query_plan += u' AND "public".pt_plan_rrhh_distribucion.id_turno = %s'
                query_production += u' AND "public".pt_produccion_terminada.id_turno = %s'
                query_rechazos += u' AND "public".nc_rechazos_cajones.id_turno = %s'

            if module_id:
                params.append(module_id)
                var_farol_plan = 38 if module_id == 1 else 37
                var_rechazos_plan = 40
                query_plan += u' AND "public".pt_plan_rrhh_distribucion.id_modulo = %s'
                query_production += u' AND "public".pt_produccion_terminada.id_modulo = %s'
                query_rechazos += u' AND "public".nc_rechazos_cajones.id_modulo = %s'

            cursor.execute(query_plan % tuple(params))
            plan = cursor.fetchall()

            cursor.execute(query_production % tuple(params))
            production = cursor.fetchall()

            accomplish_rejection = True
            if turn_id:
                cursor.execute(query_farol % tuple(params))

                farol = cursor.fetchall()

                cursor.execute(query_farol_plan % (var_farol_plan, date))
                farol_plan = cursor.fetchall()

                if len(farol) > 0 and farol[0][0] is not None and len(farol_plan) > 0 and farol_plan[0][0] is not None:
                    farol_x_millon = farol[0][0]
                    if production[0][0] is not None and production[0][0] > 0:
                        farol_x_millon = farol[0][0] / (production[0][0] / 100)

                    if farol_x_millon <= float(farol_plan[0][2]):
                        cursor.execute(query_rechazos % tuple(params))
                        rechazos = cursor.fetchall()

                        # Buscar plan de rechazos taller
                        cursor.execute(query_rechazos_plan % (var_rechazos_plan, date))
                        rechazos_plan = cursor.fetchall()

                        if rechazos[0][0] <= float(rechazos_plan[0][2]):
                            accomplish_rejection = True

                        porciento_cumplimiento = production[0][0] * 100.00
                        if plan[0][0] is not None and plan[0][0] > 0:
                            porciento_cumplimiento = (production[0][0] * 100.00) / plan[0][0]
                    else:
                        accomplish_rejection = False
                        porciento_cumplimiento = 0.0
                else:
                    accomplish_rejection = False
                    porciento_cumplimiento = 0.0

            if turn_id and not module_id:
                dict_calculations['rrhh'][date_string][turn_id] = {'val': porciento_cumplimiento,
                                                                   'accomplish_rejection': accomplish_rejection}
            elif turn_id and module_id:
                dict_calculations['rrhh'][date_string][(str(turn_id) + '-' + str(module_id))] = {
                    'val': porciento_cumplimiento, 'accomplish_rejection': accomplish_rejection}
            elif not turn_id and not module_id:
                dict_calculations['rrhh'][date_string]['ueb'] = {
                    'val': porciento_cumplimiento, 'accomplish_rejection': accomplish_rejection}

        if concept.lower_limit <= porciento_cumplimiento < concept.upper_limit and (
                accomplish_rejection or not rejection):
            return True
        else:
            return False

    def _check_te_overcompliance(self, dict_calculations, cursor, concept, date, turn_id=False, module_id=False):
        date_string = fields.Date.to_string(date)
        calculated = False
        porciento_cumplimiento = 0.0

        if date_string in dict_calculations['te']:
            if turn_id and not module_id and turn_id in dict_calculations['te'][date_string]:
                porciento_cumplimiento = dict_calculations['te'][date_string][turn_id]['val']
                calculated = True
            if turn_id and module_id and (str(turn_id) + '-' + str(module_id)) in dict_calculations['te'][date_string]:
                porciento_cumplimiento = dict_calculations['te'][date_string][(str(turn_id) + '-' + str(module_id))][
                    'val']
                calculated = True
            elif not turn_id and not module_id and 'ueb' in dict_calculations['te'][date_string]:
                porciento_cumplimiento = dict_calculations['te'][date_string]['ueb']['val']
                calculated = True
        else:
            dict_calculations['te'][date_string] = {}

        if not calculated:
            params = [date]
            query_plan = u"""SELECT
                    Sum("public".pt_plan_te_distribucion.plan)
                    FROM
                    "public".pt_plan_te_distribucion
                    WHERE
                    "public".pt_plan_te_distribucion.fecha = '%s'"""

            query_production = u"""SELECT
                    CASE WHEN (Sum("public".pt_produccion_terminada.cantidad_producida)) IS NULL THEN
                    (0) ELSE (Sum("public".pt_produccion_terminada.cantidad_producida)) END AS prod
                    FROM
                    "public".pt_produccion_terminada
                    WHERE
                    "public".pt_produccion_terminada.fecha = '%s'"""

            if turn_id:
                params.append(turn_id)
                query_plan += u' AND "public".pt_plan_te_distribucion.id_turno = %s'
                query_production += u' AND "public".pt_produccion_terminada.id_turno = %s'

            if module_id:
                params.append(module_id)
                query_plan += u' AND "public".pt_plan_te_distribucion.id_modulo = %s'
                query_production += u' AND "public".pt_produccion_terminada.id_modulo = %s'

            cursor.execute(query_plan % tuple(params))
            plan = cursor.fetchall()

            cursor.execute(query_production % tuple(params))
            production = cursor.fetchall()
            porciento_cumplimiento = production[0][0] * 100.00
            if plan[0][0] is not None and plan[0][0] > 0:
                porciento_cumplimiento = (production[0][0] * 100.00) / plan[0][0]

            if turn_id and not module_id:
                dict_calculations['te'][date_string][turn_id] = {'val': porciento_cumplimiento}
            elif turn_id and module_id:
                dict_calculations['rrhh'][date_string][(str(turn_id) + '-' + str(module_id))] = {
                    'val': porciento_cumplimiento}
            elif not turn_id and not module_id:
                dict_calculations['rrhh'][date_string]['ueb'] = {
                    'val': porciento_cumplimiento}

        if concept.lower_limit <= porciento_cumplimiento < concept.upper_limit:
            return True
        else:
            return False

    def _check_ptrc_production_overcompliance(self, dict_calculations, cursor, concept, date):
        date_string = fields.Date.to_string(date)
        calculated = False
        porciento_cumplimiento = 0.0

        if date_string in dict_calculations['ptrc']:
            if 'ueb' in dict_calculations['ptrc'][date_string]:
                porciento_cumplimiento = dict_calculations['ptrc'][date_string]['ueb']
                calculated = True
        else:
            dict_calculations['ptrc'][date_string] = {}

        if not calculated:
            cursor.execute(u"""SELECT
                              Sum("public".ptrc_plan_rrhh_distribucion.plan) AS plan
                              FROM
                              "public".ptrc_plan_rrhh_distribucion
                              WHERE
                              "public".ptrc_plan_rrhh_distribucion.fecha = '%s'""" % date)
            plan = cursor.fetchall()

            cursor.execute(u"""SELECT
                              Sum("public".ptrc_datos_productivos.cantidad) AS tr
                              FROM
                              "public".ptrc_datos_productivos
                              WHERE
                              "public".ptrc_datos_productivos.id_referencia = 16 AND
                              "public".ptrc_datos_productivos.fecha = '%s'""" % date)
            produccion = cursor.fetchall()

            porciento_cumplimiento = produccion[0][0] * 100.00
            if plan[0][0] is not None and plan[0][0] > 0:
                porciento_cumplimiento = (produccion[0][0] * 100.00) / plan[0][0]

            dict_calculations['ptrc'][date_string]['ueb'] = porciento_cumplimiento

        if concept.lower_limit <= porciento_cumplimiento < concept.upper_limit:
            return True
        else:
            return False

    def _check_hebra_production_overcompliance(self, dict_calculations, cursor, concept, date, turn_id=False):
        date_string = fields.Date.to_string(date)
        calculated = False
        porciento_cumplimiento = 0.0

        if date_string in dict_calculations['hebra']:
            if turn_id and turn_id in dict_calculations['hebra'][date_string]:
                porciento_cumplimiento = dict_calculations['hebra'][date_string][turn_id]
                calculated = True
            elif not turn_id and 'ueb' in dict_calculations['hebra'][date_string]:
                porciento_cumplimiento = dict_calculations['hebra'][date_string]['ueb']
                calculated = True
        else:
            dict_calculations['hebra'][date_string] = {}

        if not calculated:

            query_plan = u"""SELECT
                              CASE WHEN SUM ("public".plan_produccion_hebra.hebra) IS NULL THEN (0) ELSE SUM ("public".plan_produccion_hebra.hebra)END AS hebra
                              FROM
                              "public".plan_produccion_hebra
                              WHERE
                              "public".plan_produccion_hebra.fecha = '%s'"""

            query_production = u"""SELECT
                              Sum("public".hb_produccion.hebra) AS hebra
                              FROM
                              "public".hb_produccion
                              WHERE
                              "public".hb_produccion.fecha = '%s'"""

            if turn_id:
                query_plan += u' AND "public".plan_produccion_hebra.id_turno = %s'
                query_production += u' AND "public".hb_produccion.id_turno = %s'
                params = [date_string, turn_id]
            else:
                params = [date_string]

            cursor.execute(query_plan % tuple(params))
            plan = cursor.fetchall()

            cursor.execute(query_production % tuple(params))
            produccion = cursor.fetchall()

            porciento_cumplimiento = produccion[0][0] * 100.00
            if plan[0][0] is not None and plan[0][0] > 0:
                porciento_cumplimiento = (produccion[0][0] * 100.00) / plan[0][0]

            if turn_id:
                dict_calculations['hebra'][date_string][turn_id] = porciento_cumplimiento
            else:
                dict_calculations['hebra'][date_string]['ueb'] = porciento_cumplimiento

        if concept.lower_limit <= porciento_cumplimiento < concept.upper_limit:
            return True
        else:
            return False

    def _get_day_string(self, day):
        if day == 0:
            return _('Monday')
        elif day == 1:
            return _('Tuesday')
        elif day == 2:
            return _('Wednesday')
        elif day == 3:
            return _('Thursday')
        elif day == 4:
            return _('Friday')
        elif day == 5:
            return _('Saturday')
        elif day == 6:
            return _('Sunday')

    def _get_month_string(self, month):
        if month == 1:
            return _('January')
        elif month == 2:
            return _('February')
        elif month == 3:
            return _('March')
        elif month == 4:
            return _('April')
        elif month == 5:
            return _('May')
        elif month == 6:
            return _('June')
        elif month == 7:
            return _('July')
        elif month == 8:
            return _('August')
        elif month == 9:
            return _('September')
        elif month == 10:
            return _('October')
        elif month == 11:
            return _('November')
        elif month == 12:
            return _('December')


HrTureiWeeklySmokingDeliveryList('report.hr_turei.weekly_smoking_delivery_list', 'hr_turei.weekly_smoking_delivery_wzd')
