# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _, SUPERUSER_ID, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from calendar import Calendar
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import pytz
import pkg_resources

month_dic = {'01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril', '05': 'mayo', '06': 'junio',
             '07': 'julio', '08': 'agosto', '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'}


class CalendarReportUtils(models.AbstractModel):
    _name = "l10n_cu_calendar.report_utils"

    def _get_categ_children(self, list, parent_id):
        task_category = self.env['l10n_cu_calendar.task_category']
        for catg in task_category.search([('parent_id', '=', parent_id)]):
            list.append(catg)
            self._get_categ_children(list, catg.id)

    @api.model
    def _compute_resume_values(self, data):
        report_obj = self.env['report']
        data['enable_editor'] = 0
        employee_obj = self.env['hr.employee']
        model = self.env.context.get('active_model')

        event_obj = self.env['calendar.event']
        attendee_obj = self.env['calendar.attendee']
        date_start = data['date_start']

        date_end = data['date_end']
        employee = self.sudo(user=SUPERUSER_ID).env['hr.employee'].browse(data['employee_id'])
        indv_plan_res=[{'id':'','name':'','job':'','manager_name':'','manager_job':'','mes':'','anno':'','main_task_list':[],'login':'','calendar':[]}]
        # RESUMEN CUALITATIVO / RESUME
        indv_plan_res[0]['resumen'] = data['text']

        #INCIALIZAMOS
        indv_plan_res[0]['name'] = employee.name
        indv_plan_res[0]['job'] = employee.job_id.name

        # OTROS DATOS
        indv_plan_res[0]['manager_name'] = employee.parent_id.name
        indv_plan_res[0]['manager_job'] = employee.parent_id.job_id.name
        indv_plan_res[0]['area'] = employee.department_id.name
        indv_plan_res[0]['periodo'] = data['periodo']

        partner_id = employee.user_id.partner_id.id
        done_task = 0
        plan_task = 0
        not_done_task_list = []
        modified_task_list = []
        extra_plan_task = 0
        extra_plan_list = []
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')

        attende_list = attendee_obj.search(
            [('partner_id', '=', partner_id), ('date_start', '>=', date_start), ('date_start', '<=', date_end),
             ('recurrency', '=', False),('state', 'in', ('accepted','done','not_done'))])

        for a in attende_list:
            if a.event_id.active:
                # localice t.event_id.start
                start_date = pytz.UTC.localize(fields.Datetime.from_string(a.event_id.start))  # Add "+hh:mm" timezone
                start_date = start_date.astimezone(timezone)  # transform "+hh:mm" timezone
                start_date = fields.Datetime.to_string(start_date)  # convert to string

                if a['state'] == 'done':
                    done_task += 1

                if a['state'] == 'not_done':
                    res = {}
                    res['name'] = a.event_id.name + "(" + start_date[:10][8:] + ")"
                    res['cause'] = a.cause
                    not_done_task_list.append(res)

                if a.event_id.type == 'extra':
                    res = {}
                    res['name'] = a.event_id.name
                    res['start'] = start_date[:10][8:]
                    res['hour_start'] = 'T/D' if a.event_id.allday else start_date[11:][:5]
                    employee = False
                    if a.event_id.extra_plan_origin.employee:
                        employee = employee_obj.search([('user_id.partner_id.id', '=', a.event_id.extra_plan_origin.id)])
                    res['user_id'] = employee.job_id.name if employee and employee.job_id.name else a.event_id.extra_plan_origin.name
                    res['user_id'] = res['user_id'] if res['user_id'] else a.event_id.directed_by_job
                    res['cause'] = a.event_id.extra_plan_cause
                    extra_plan_list.append(res)
                    extra_plan_task += 1
                else:
                    plan_task += 1

        fecha = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        year_last_day = str(fecha.year) + '-12-31'
        year_first_day = str(fecha.year) + '-01-01'

        extra_plan_task = len(extra_plan_list)
        attende_list = attendee_obj.search([('partner_id', '=', partner_id), ('date_start', '>=', year_first_day), ('date_start', '<=', year_last_day),
             ('recurrency', '=', False),('state', 'in', ('accepted','done','not_done'))])
        for a in attende_list:
            if a.event_id.active:
                res = {}
                res['name'] = a.event_id.name
                res['modifications'] = ''
                modified = False
                list_trace_field = ['local_id', 'start_date', 'start_datetime']  # campos a trace
                datetime_list_old = {}  # lista pra guardar las veces que fue modificada la fecha/hora de la tarea
                datetime_list_new = {}  # lista pra guardar las veces que fue modificada la fecha/hora de la tarea
                local_list = []  # lista para guardar las veces que fue modificado el local de la tarea
                messages = self.env['mail.message'].search([('model', '=', 'calendar.event'), ('res_id', '=', a.event_id.id)], order='id asc')
                status_ok = False
                status_label = dict(self.env['calendar.event'].fields_get(allfields=['state'])['state']['selection'])['draft']
                for msg in messages:
                    for trace in msg.sudo().tracking_value_ids:
                        if trace.field == 'state':
                            # Tener en cuenta solo cambios realizados despues de primera vez confirmada la tarea
                            # El estado se guarda en la traza con su label traducido
                            if trace.new_value_char and trace.new_value_char != status_label:
                                status_ok = True

                        # buscar especificamente los cambio en la fecha y la hora y en el local
                        if status_ok and trace.field in list_trace_field:
                            if trace.old_value_datetime or trace.new_value_datetime:
                                if trace.new_value_datetime:
                                    datetime_list_new = {'value': trace.new_value_datetime, 'field': trace.field}
                                if not datetime_list_old and trace.old_value_datetime and date_start <= trace.old_value_datetime <= date_end:
                                    datetime_list_old = {'value': trace.old_value_datetime, 'field': trace.field}
                                    modified = True
                            if trace.old_value_char and not local_list:
                                local_list.append(trace.new_value_char)
                                modified = True
                        res['user'] = msg.create_uid.partner_id.name
                # format modifications
                if datetime_list_old and datetime_list_new:
                    old_value_datetime = datetime_list_old if datetime_list_old else False

                    if old_value_datetime.get('field') and old_value_datetime.get('field') != 'start_date':
                        # localice old_value_datetime
                        old_date = pytz.UTC.localize(
                            fields.Datetime.from_string(old_value_datetime['value']))  # Add "+hh:mm" timezone
                        old_date = old_date.astimezone(timezone)  # transform "+hh:mm" timezone
                        old_value_datetime = fields.Datetime.to_string(old_date)  # convert to string
                        old_hour = old_value_datetime[11:][:5]
                    else:
                        old_hour = 'T/D'
                        old_value_datetime = old_value_datetime['value']

                    new_value_datetime = datetime_list_new if datetime_list_new else False
                    if new_value_datetime.get('field') and new_value_datetime.get('field') != 'start_date':
                        # localice new_value_datetime
                        new_date = pytz.UTC.localize(
                            fields.Datetime.from_string(new_value_datetime['value']))  # Add "+hh:mm" timezone
                        new_date = new_date.astimezone(timezone)  # transform "+hh:mm" timezone
                        new_value_datetime = fields.Datetime.to_string(new_date)  # convert to string
                        new_hour = new_value_datetime[11:][:5]
                    else:
                        new_hour = 'T/D'
                        new_value_datetime = new_value_datetime['value']
                    if not date_start <= new_value_datetime[:10] <= date_end:
                        if a.event_id.type != 'extra':
                            plan_task += 1
                        else:
                            extra_plan_task += 1
                    res['modifications'] += 'Del ' + old_value_datetime[:10][8:] + ' de ' + month_dic[old_value_datetime[:10][5:7]] + \
                                            ' a las ' + old_hour + ' para el ' + new_value_datetime[:10][8:] + ' de ' + \
                                            month_dic[new_value_datetime[:10][5:7]] + ' a las ' + new_hour
                if local_list:
                    res['modifications'] += local_list[0] if (datetime_list_new or datetime_list_old) else ''

                if (modified and self.env.user.company_id.tasks_postponed_only and (new_value_datetime and date_end + ' 23:59:59' < new_value_datetime) and old_value_datetime) or (modified and not self.env.user.company_id.tasks_postponed_only):
                    employee = False
                    if a.event_id.modification_origin:
                        if a.event_id.modification_origin.employee:
                            employee = employee_obj.search([('user_id.partner_id.id', '=', a.event_id.modification_origin.id)])
                        employee = employee.job_id.name if employee and employee.job_id.name else a.event_id.modification_origin.name
                    res['user'] = employee if employee else res['user']
                    res['cause'] = a.event_id.modification_cause if a.event_id.modification_cause else ''
                    modified_task_list.append(res)

        indv_plan_res[0]['plan_task'] = plan_task
        indv_plan_res[0]['done_task'] = done_task
        indv_plan_res[0]['not_done_task_list'] = not_done_task_list
        indv_plan_res[0]['not_done_task'] = len(not_done_task_list)
        indv_plan_res[0]['modified_task_list'] = modified_task_list
        indv_plan_res[0]['modified_task'] = len(modified_task_list)
        indv_plan_res[0]['extra_plan_task'] = extra_plan_task
        indv_plan_res[0]['extra_plan_list'] = extra_plan_list

        return indv_plan_res

    @api.model
    def _compute_group_resume_values(self, data=None):
        data['enable_editor'] = 0
        event_obj = self.env['calendar.event']
        employee_obj = self.env['hr.employee']
        date_start = data['date_start']
        date_end = data['date_end']
        org_group = self.env['l10n_cu_calendar.org_group'].browse(data['group_id'])

        # IMPORTANTE!!
        gruop_plan_res=[{'id':'','name':'','mes':'','anno':'', 'group_chief':'','group_chief_job':'','periodo':''}]
        # se toman las tareas que no son recurrentes en el rango de fechas
        event_ids = event_obj.search([('attendees_group_ids','in',org_group.id),('start','>=',date_start),('start','<=',date_end),('recurrency','=',False)])
        unfulfilled_task_list = []
        extra_plan_list = []
        modified_task_list = []
        fulfilled_task = 0
        plan_task = 0
        extra_plan_task = 0
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        for e in event_ids:
            # take the user timezone
            start_date = pytz.UTC.localize(fields.Datetime.from_string(e.start))  # Add "+hh:mm" timezone
            start_date = start_date.astimezone(timezone)  # transform "+hh:mm" timezone
            start_date = fields.Datetime.to_string(start_date)  # convert to string
            if e.state == 'unfulfilled':
                res = {}
                res['name'] = e.name + "(" + start_date[:10][8:] + ")"
                res['cause'] = e.unfulfilled_cause
                employee = False
                if e.unfulfilled_origin.employee:
                    employee = employee_obj.search([('user_id.partner_id.id', '=', e.unfulfilled_origin.id)])
                res['user_id'] = employee.job_id.name if employee and employee.job_id.name else e.unfulfilled_origin.name
                unfulfilled_task_list.append(res)
            elif e.state == 'fulfilled':
                    fulfilled_task += 1

            if e.type == 'extra':
                res = {}
                res['name'] = e.name
                res['start'] = start_date[:10][8:]
                res['hour_start'] = 'T/D' if start_date[11:][:5] == '00:00' else start_date[11:][:5]
                employee = False
                if e.extra_plan_origin.employee:
                    employee = employee_obj.search([('user_id.partner_id.id', '=', e.extra_plan_origin.id)])
                res['user_id'] = employee.job_id.name if employee and employee.job_id.name else e.extra_plan_origin.name
                res['user_id'] = res['user_id'] if res['user_id'] else e.directed_by_job
                res['cause'] = e.extra_plan_cause
                extra_plan_list.append(res)
                extra_plan_task += 1
            else:
                plan_task += 1

        fecha = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        year_last_day = str(fecha.year) + '-12-31'
        year_first_day = str(fecha.year) + '-01-01'
        event_ids = event_obj.search([('attendees_group_ids','in',org_group.id),('start','>=',year_first_day),('start','<=',year_last_day),('recurrency','=',False)])
        for e in event_ids:
            res = {}
            res['name'] = e.name
            res['modifications'] = ''
            modified = False
            list_trace_field = ['local_id', 'start_date', 'start_datetime']  # campos a trace
            datetime_list_old = {}  # lista pra guardar las veces que fue modificada la fecha/hora de la tarea
            datetime_list_new = {}  # lista pra guardar las veces que fue modificada la fecha/hora de la tarea
            local_list = []  # lista para guardar las veces que fue modificado el local de la tarea
            messages = self.env['mail.message'].search(
                [('model', '=', 'calendar.event'), ('res_id', '=', e.id)], order='id asc')
            status_ok = False
            lang_code = (tools.config.get('load_language') or 'en_US').split(',')[0]
            status_label = dict(self.env['calendar.event'].fields_get(allfields=['state'])['state']['selection'])[
                'draft']
            status_label_default = dict(self.env['calendar.event'].with_context(lang=lang_code).fields_get(allfields=['state'])['state']['selection'])[
                'draft']
            for msg in messages:
                for trace in msg.sudo().tracking_value_ids:
                    if trace.field == 'state':
                        # Tener en cuenta solo cambios realizados despues de primera vez confirmada la tarea
                        # El estado se guarda en la traza con su label traducido
                        if trace.new_value_char and (trace.new_value_char != status_label and trace.new_value_char != status_label_default):
                            status_ok = True

                    # buscar especificamente los cambio en la fecha y la hora y en el local
                    if status_ok and trace.field in list_trace_field:
                        if trace.old_value_datetime or trace.new_value_datetime:
                            if trace.new_value_datetime:
                                datetime_list_new = {'value': trace.new_value_datetime, 'field': trace.field}
                            if not datetime_list_old and trace.old_value_datetime and date_start <= trace.old_value_datetime <= date_end:
                                datetime_list_old = {'value': trace.old_value_datetime, 'field': trace.field}
                                modified = True
                        if trace.old_value_char and not local_list:
                            local_list.append(trace.new_value_char)
                            modified = True
                    res['user'] = msg.create_uid.partner_id.name
            # format modifications
            if datetime_list_old and datetime_list_new:
                old_value_datetime = datetime_list_old if datetime_list_old else False

                if old_value_datetime.get('field') and old_value_datetime.get('field') != 'start_date':
                    # localice old_value_datetime
                    old_date = pytz.UTC.localize(
                        fields.Datetime.from_string(old_value_datetime['value']))  # Add "+hh:mm" timezone
                    old_date = old_date.astimezone(timezone)  # transform "+hh:mm" timezone
                    old_value_datetime = fields.Datetime.to_string(old_date)  # convert to string
                    old_hour = old_value_datetime[11:][:5]
                else:
                    old_hour = 'T/D'
                    old_value_datetime = old_value_datetime['value']

                new_value_datetime = datetime_list_new if datetime_list_new else False
                if new_value_datetime.get('field') and new_value_datetime.get('field') != 'start_date':
                    # localice new_value_datetime
                    new_date = pytz.UTC.localize(
                        fields.Datetime.from_string(new_value_datetime['value']))  # Add "+hh:mm" timezone
                    new_date = new_date.astimezone(timezone)  # transform "+hh:mm" timezone
                    new_value_datetime = fields.Datetime.to_string(new_date)  # convert to string
                    new_hour = new_value_datetime[11:][:5]
                else:
                    new_hour = 'T/D'
                    new_value_datetime = new_value_datetime['value']
                if not date_start <= new_value_datetime <= date_end:
                    if e.type != 'extra':
                        plan_task += 1
                    else:
                        extra_plan_task += 1

                res['modifications'] += 'Del ' + old_value_datetime[:10][8:] + ' de ' + month_dic[old_value_datetime[:10][5:7]] + \
                                        ' a las ' + old_hour + ' para el ' + new_value_datetime[:10][8:] + ' de ' + \
                                        month_dic[new_value_datetime[:10][5:7]] + ' a las ' + new_hour
            if local_list:
                res['modifications'] += local_list[0] if (datetime_list_new or datetime_list_old) else ''

            if (modified and self.env.user.company_id.tasks_postponed_only and (new_value_datetime and date_end + ' 23:59:59' < new_value_datetime) and old_value_datetime) or (modified and not self.env.user.company_id.tasks_postponed_only):
                employee = False
                if e.modification_origin:
                    if e.modification_origin.employee:
                        employee = employee_obj.search([('user_id.partner_id.id', '=', e.modification_origin.id)])
                    employee = employee.job_id.name if employee and employee.job_id.name else e.modification_origin.name
                res['user'] = employee if employee else res['user']
                res['cause'] = e.modification_cause if e.modification_cause else ''
                modified_task_list.append(res)

        # RESUMEN CUALITATIVO / RESUME
        gruop_plan_res[0]['resumen'] = data['text']
        gruop_plan_res[0]['monthly'] = data['monthly']

        # INCIALIZAMOS
        gruop_plan_res[0]['name'] = org_group.name
        gruop_plan_res[0]['unfulfilled_task_list'] = unfulfilled_task_list
        gruop_plan_res[0]['unfulfilled_task'] = len(unfulfilled_task_list)
        gruop_plan_res[0]['modified_task_list'] = modified_task_list
        gruop_plan_res[0]['modified_task'] = len(modified_task_list)
        gruop_plan_res[0]['extra_plan_list'] = extra_plan_list
        gruop_plan_res[0]['extra_plan_task'] = extra_plan_task
        gruop_plan_res[0]['fulfilled_task'] = fulfilled_task
        gruop_plan_res[0]['plan_task'] = plan_task
        gruop_plan_res[0]['periodo'] = data['periodo']

        return gruop_plan_res

    @api.model
    def _compute_obj_cat_monthly_plan(self, data):
        category_list = []
        principal_task_list = []
        global_list = []
        org_group = self.env['l10n_cu_calendar.org_group'].browse(data['group_id'])
        date_start = data['date_start']
        date_end = data['date_end']
        date = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        year_last_day = str(date.year) + '-12-31'
        year_first_day = str(date.year) + '-01-01'
        event_obj = self.env['calendar.event']
        gruop_plan_res = [{'id': '', 'name': '', 'mes': '', 'anno': '', 'task_list': [], 'principal_task_list': [],
                           'group_chief': '', 'group_chief_job': '', 'periodo': ''}]

        for catg in self.env['l10n_cu_calendar.task_category'].search([('parent_id', '=', False)]):
            global_list.append(catg)
            self._get_categ_children(global_list, catg.id)

        for catg in global_list:
            if catg.has_task(group_id=org_group.id, date_start=date_start, date_end=date_end):
                res = {}
                res['id'] = catg.id
                res['name'] = catg.name
                task_list = []

                # Es necesario buscar las posibles tareas padres que no tienen fecha en el periodo mensual de busqueda actual
                # y que tienen hijos que si tienen fecha en el periodo mensual de busqueda actual, esto asegura que las tareas
                # de aseguramiento cuya tarea principal no tiene fecha en el periodo de busqueda en cuestion puedan mostrarse,
                # ya que en la busqueda recursiva de otra forma no se mostrarian. No es posible hacer esta consulta en solo un
                # search debido a que los virtual_ids de las tareas recurrentes causan problemas
                # a domains de tipo ('parent_id', 'in', ['195-20211213140000'])
                out_range_parents = event_obj.with_context(virtual_id=False).search(
                    [('child_ids', '!=', False), ('stop', '>=', year_first_day),
                     ('start', '<=', year_last_day), '|', '|', ('start', '>', date_end), ('stop', '<', date_start),
                     ('attendees_group_ids', 'not in', org_group.id)])

                event_ids = event_obj.search(
                    [('attendees_group_ids', 'in', org_group.id), ('stop', '>=', date_start),
                     ('start', '<=', date_end), ('category_id', '=', catg.id), ('objective_id', '=', None),
                     '|', ('parent_id', '=', False), ('parent_id', 'in', out_range_parents.ids)])

                timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                parent_list = self._format_monthly_plan(event_ids, date_start, date_end, timezone)
                count = 1
                for task in parent_list:
                    task['no'] = str(count)
                    task_list.append(task)
                    self._search_assurance_monthly_plan(org_group.id, task, task_list, date_start, date_end, timezone)
                    count += 1

                res['task_list'] = task_list
                category_list.append(res)

                # filtrar tareas principales
                for task in task_list:
                    if task['priority'] == '2' and task['name'] not in principal_task_list:
                        principal_task_list.append(task)

                for obj in catg.objective_ids:
                    if obj.has_task(group_id=org_group.id, date_start=date_start, date_end=date_end):
                        res_obj = {}
                        res_obj['name'] = obj.name
                        task_list_obj = []

                        # Es necesario buscar las posibles tareas padres que no tienen fecha en el periodo mensual de busqueda actual
                        # y que tienen hijos que si tienen fecha en el periodo mensual de busqueda actual, esto asegura que las tareas
                        # de aseguramiento cuya tarea principal no tiene fecha en el periodo de busqueda en cuestion puedan mostrarse,
                        # ya que en la busqueda recursiva de otra forma no se mostrarian. No es posible hacer esta consulta en solo un
                        # search debido a que los virtual_ids de las tareas recurrentes causan problemas
                        # a domains de tipo ('parent_id', 'in', ['195-20211213140000'])
                        out_range_parents = event_obj.with_context(virtual_id=False).search(
                            [('child_ids', '!=', False), ('stop', '>=', year_first_day),
                             ('start', '<=', year_last_day), '|', '|', ('start', '>', date_end),
                             ('stop', '<', date_start), ('attendees_group_ids', 'not in', org_group.id)])

                        # se toman las tareas de la categoria que no son recurrentes en el rango de fechas
                        event_ids = event_obj.search([('attendees_group_ids', 'in', org_group.id),
                                                      ('stop', '>=', date_start), ('start', '<=', date_end),
                                                      ('objective_id', '=', obj.id), '|', ('parent_id', '=', False),
                                                      ('parent_id', 'in', out_range_parents.ids)])

                        parent_list = self._format_monthly_plan(event_ids, date_start, date_end, timezone)
                        count = 1
                        for task in parent_list:
                            task['no'] = str(count)
                            task_list_obj.append(task)
                            self._search_assurance_monthly_plan(org_group.id, task, task_list_obj, date_start, date_end, timezone)
                            count += 1

                        if len(task_list_obj):
                            res_obj['task_list'] = task_list_obj
                            category_list.append(res_obj)

                        # filtrar tareas principales
                        for task in task_list_obj:
                            if task['priority'] == '2' and task['name'] not in principal_task_list:
                                principal_task_list.append(task)

        gruop_plan_res[0]['name'] = org_group.name.upper()
        gruop_plan_res[0]['periodo'] = data['periodo'].upper()
        gruop_plan_res[0]['category_list'] = category_list
        gruop_plan_res[0]['principal_task_list'] = principal_task_list
        gruop_plan_res[0]['approved_by'] = data['approved_by'] if data['approved_by'] else org_group.partner_id.name
        gruop_plan_res[0]['approved_function'] = data['approved_function'] if data[
            'approved_by'] else org_group.partner_id.function
        gruop_plan_res[0]['group_chief'] = data['elaborated_by'] if data['elaborated_by'] else org_group.partner_id.name
        gruop_plan_res[0]['group_chief_job'] = data['elaborated_function'] if data[
            'elaborated_by'] else org_group.partner_id.function

        return gruop_plan_res

    def _search_assurance_monthly_plan(self, group_id, parent_task, task_list, date_start, date_end, timezone):
        count = 1
        tasks = self.env['calendar.event'].search([('attendees_group_ids', 'in', group_id), ('parent_id', 'in', parent_task['ids']), ('stop', '>=', date_start), ('start', '<=', date_end)])
        parent_list = self._format_monthly_plan(tasks, date_start, date_end, timezone)
        for task in parent_list:
            task['no'] = parent_task['no'] + '.' + str(count)
            task_list.append(task)
            self._search_assurance_monthly_plan(group_id, task, task_list, date_start, date_end, timezone)
            count += 1

    def _format_monthly_plan(self, tasks, date_start, date_end, timezone):
        month = date_start[:7][5:]
        task_list = []
        witness_list = []
        for e in tasks:
            res = {'ids':[]}
            startdate = pytz.UTC.localize(fields.Datetime.from_string(e.start))
            start = startdate.astimezone(timezone)  # transform "+hh:mm" timezone
            start = fields.Datetime.to_string(start)  # convert to string

            stopdate = pytz.UTC.localize(fields.Datetime.from_string(e.stop))
            stop = startdate.astimezone(timezone)  # transform "+hh:mm" timezone
            stop = fields.Datetime.to_string(stop)  # convert to string

            # buscar en witness_list si ya la tarea ha sido insertada
            if not e.hide_time_in_report:
                hour = 'Hora: T/D' if e.allday else 'Hora: ' + start[11:][:5]
            else:
                hour = ''
            local = 'Lugar: ' + e.local_id.name if e.local_id else ''
            chain = e.name + ' ' + hour + ' ' + local
            if chain in witness_list:
                # si ha sido insertada entonces tiene otra fecha en el mismo periodo
                # adicionar la fecha en la lista de fechas
                if start[:7][5:] == stop[:7][5:]:
                    if start[:10][8:] == stop[:10][8:]:
                        task_list[witness_list.index(chain)]['date'].append(start[:10][8:])
                    else:
                        task_list[witness_list.index(chain)]['date'].append(start[:10][8:] + '-' + stop[:10][8:])
                else:
                    if start[:7][5:] == month:
                        task_list[witness_list.index(chain)]['date'].append(start[:10][8:] + '-')
                    elif stop[:7][5:] == month:
                        task_list[witness_list.index(chain)]['date'].append('-' + stop[:10][8:])
                    else:
                        task_list[witness_list.index(chain)]['date'].append(date_start[:10][8:] + '-' + date_end[:10][8:])

                if isinstance(e.id, int):
                    res['ids'].append(e.id)
            else:
                if isinstance(e.id, int):
                    res['ids'] = [e.id]
                res['name'] = e.name
                res['priority'] = e.priority
                res['date'] = []
                if start[:7][5:] == stop[:7][5:]:
                    if start[:10][8:] == stop[:10][8:]:
                        res['date'].append(start[:10][8:])
                    else:
                        res['date'].append(start[:10][8:] + '-' + stop[:10][8:])
                else:
                    if start[:7][5:] == month:
                        res['date'].append(start[:10][8:] + '-')
                    elif stop[:7][5:] == month:
                        res['date'].append('-' + stop[:10][8:])
                    else:
                        res['date'].append(date_start[:10][8:] + '-' + date_end[:10][8:])
                res['display_start'] = e.display_start
                res['hour'] = 'Hora: T/D' if e.allday else 'Hora: ' + start[11:][:5]
                res['local'] = 'Lugar: ' + e.local_id.name if e.local_id else False
                res['directed_for'] = e.directed_by_job
                res['participants_char'] = e.participants_char()
                task_list.append(res)
                witness_list.append(chain)

        for t in task_list:
            date_str = ''
            if len(t['date']):
                if len(t['date']) > 1:
                    t['date'].sort()
                    i = 0
                    for d in t['date']:
                        if 0 < i < (len(t['date']) - 1):
                            date_str += ', '
                        elif i > 0:
                            date_str += ' y '
                        date_str += d
                        i += 1
                else:
                    date_str = t['date'][0]

            t['date'] = date_str

        return task_list

    @api.model
    def _compute_monthly_plan(self, data):
        org_group = self.env['l10n_cu_calendar.org_group'].browse(data['group_id'])
        date_start = data['date_start']
        date_end = data['date_end']
        event_obj = self.env['calendar.event']
        gruop_plan_res = [{'id': '', 'name': '', 'mes': '', 'anno': '', 'task_list': [], 'principal_task_list': [],
                           'group_chief': '', 'group_chief_job': '', 'periodo': ''}]

        date = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        year_last_day = str(date.year) + '-12-31'
        year_first_day = str(date.year) + '-01-01'
        # Es necesario buscar las posibles tareas padres que no tienen fecha en el periodo mensual de busqueda actual
        # y que tienen hijos que si tienen fecha en el periodo mensual de busqueda actual, esto asegura que las tareas
        # de aseguramiento cuya tarea principal no tiene fecha en el periodo de busqueda en cuestion puedan mostrarse,
        # ya que en la busqueda recursiva de otra forma no se mostrarian. No es posible hacer esta consulta en solo un
        # search debido a que los virtual_ids de las tareas recurrentes causan problemas
        # a domains de tipo ('parent_id', 'in', ['195-20211213140000'])
        out_range_parents = event_obj.with_context(virtual_id=False).search(
            [('child_ids', '!=', False), ('stop', '>=', year_first_day), ('start', '<=', year_last_day), '|', '|', ('start', '>', date_end), ('stop', '<', date_start),
             ('attendees_group_ids', 'not in', org_group.id)])

        event_ids = event_obj.search([('attendees_group_ids', 'in', org_group.id), ('stop', '>=', date_start),
                                      ('start', '<=', date_end), '|', ('parent_id', '=', False), ('parent_id', 'in', out_range_parents.ids)])
        task_list = []
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        parent_list = self._format_monthly_plan(event_ids, date_start, date_end, timezone)
        count = 1
        for task in parent_list:
            task['no'] = str(count)
            task_list.append(task)
            self._search_assurance_monthly_plan(org_group.id, task, task_list, date_start, date_end, timezone)
            count += 1

        # filtrar tareas principales
        principal_task_list = []
        for task in task_list:
            if task['priority'] == '2' and task['name'] not in principal_task_list:
                principal_task_list.append(task)

        gruop_plan_res[0]['name'] = org_group.name.upper()
        gruop_plan_res[0]['periodo'] = data['periodo'].upper()
        gruop_plan_res[0]['task_list'] = task_list
        gruop_plan_res[0]['principal_task_list'] = principal_task_list
        gruop_plan_res[0]['approved_by'] = data['approved_by'] if data['approved_by'] else org_group.partner_id.name
        gruop_plan_res[0]['approved_function'] = data['approved_function'] if data[
            'approved_by'] else org_group.partner_id.function
        gruop_plan_res[0]['group_chief'] = data['elaborated_by'] if data[
            'elaborated_by'] else org_group.partner_id.name
        gruop_plan_res[0]['group_chief_job'] = data['elaborated_function'] if data[
            'elaborated_by'] else org_group.partner_id.function

        return gruop_plan_res

    def _format_task_annual_plan(self, tasks, timezone):
        parent_list = []
        witness_list = []
        for task in tasks:
            startdate = pytz.UTC.localize(fields.Datetime.from_string(task.start))
            start = startdate.astimezone(timezone)
            start = fields.Datetime.to_string(start)

            stopdate = pytz.UTC.localize(fields.Datetime.from_string(task.stop))
            stop = stopdate.astimezone(timezone)
            stop = fields.Datetime.to_string(stop)

            # search if there is a task with the same name, hour and local in the witness_list
            if not task.hide_time_in_report:
                hour = 'Hora: T/D' if task.allday else 'Hora: ' + start[11:][:5]
            else:
                hour = ''
            local = 'Lugar: ' + task.local_id.name if task.local_id else ''
            chain = task.name + ' ' + hour + ' ' + local
            if chain in witness_list:
                if start[:7][5:] == stop[:7][5:]:
                    if start[:10][8:] == stop[:10][8:]:
                        parent_list[witness_list.index(chain)][start[:7][5:]].append(start[:10][8:])
                    else:
                        parent_list[witness_list.index(chain)][start[:7][5:]].append(start[:10][8:] + '-' + stop[:10][8:])
                else:
                    parent_list[witness_list.index(chain)][start[:7][5:]].append(start[:10][8:] + '-')
                    parent_list[witness_list.index(chain)][stop[:7][5:]].append('-' + stop[:10][8:])

                if isinstance(task.id, int):
                    parent_list[witness_list.index(chain)]['ids'].append(task.id)
            else:
                # Add the task to the task_list and the chain to the witness_list
                t = {'ids': [], 'name': '', 'directed_for': '', 'participants_char': '', '01': [], '02': [],
                     '03': [], '04': [], '05': [], '06': [], '07': [], '08': [], '09': [], '10': [],
                     '11': [], '12': []}
                if isinstance(task.id, int):
                    t['ids'].append(task.id)
                t['name'] = task.name
                t['directed_for'] = task.directed_by_job
                t['participants_char'] = task.participants_char()
                t['hour'] = hour
                t['local'] = local
                if start[:7][5:] == stop[:7][5:]:
                    t[start[:7][5:]].append(start[:10][8:] if start[:10][8:] == stop[:10][8:] \
                        else start[:10][8:] + '-' + stop[:10][8:])
                else:
                    t[start[:7][5:]].append(start[:10][8:] + '-')
                    t[stop[:7][5:]].append('-' + stop[:10][8:])

                parent_list.append(t)
                witness_list.append(chain)

        for t in parent_list:
            for m in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                date_str = ''
                if len(t[m]):
                    if len(t[m]) > 1:
                        t[m].sort()
                        i = 0
                        for d in t[m]:
                            if 0 < i < (len(t[m]) - 1):
                                date_str += ', '
                            elif i > 0:
                                date_str += ' y '
                            date_str += d
                            i += 1
                    else:
                        date_str = t[m][0]

                t[m] = date_str

        return parent_list

    def _search_assurance_annual_plan(self, group_id, parent_task, task_list, date_start, date_end, timezone):
        count = 1
        tasks = self.env['calendar.event'].search([('attendees_group_ids', 'in', group_id), ('parent_id', 'in', parent_task['ids']), ('stop', '>=', date_start), ('start', '<=', date_end)])
        parent_list = self._format_task_annual_plan(tasks, timezone)
        for task in parent_list:
            task['no'] = parent_task['no'] + '.' + str(count)
            task_list.append(task)
            self._search_assurance_annual_plan(group_id, task, task_list, date_start, date_end, timezone)
            count += 1

    @api.model
    def _compute_annual_plan(self, data):
        date_start = data['date_start']
        date_end = data['date_end']
        org_group = self.env['l10n_cu_calendar.org_group'].browse(data['group_id'])
        event_obj = self.env['calendar.event']
        gruop_plan_res = [{'id': '', 'name': '', 'periodo': '',
                           'category_list': [],
                           'group_chief': '', 'group_chief_job': '', }]
        task_category = self.env['l10n_cu_calendar.task_category']
        category_list = []
        global_list = []
        for catg in task_category.search([('parent_id', '=', False)]):
            global_list.append(catg)
            self._get_categ_children(global_list, catg.id)

        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        for catg in global_list:
            if catg.has_task(group_id=org_group.id, date_start=date_start, date_end=date_end):
                res = {}
                res['id'] = catg.id
                res['name'] = catg.name
                task_list = []
                tasks = event_obj.search(
                        [('attendees_group_ids', 'in', org_group.id), ('category_id', '=', catg.id),
                         ('stop', '>=', date_start), ('start', '<=', date_end),
                         ('objective_id', '=', None), ('parent_id', '=', False)])

                parent_list = self._format_task_annual_plan(tasks, timezone)
                count = 1
                for task in parent_list:
                    task['no'] = str(count)
                    task_list.append(task)
                    self._search_assurance_annual_plan(org_group.id, task, task_list, date_start, date_end, timezone)
                    count += 1

                res['task_list'] = task_list
                category_list.append(res)

                for obj in catg.objective_ids:
                    if obj.has_task(group_id=org_group.id, date_start=date_start, date_end=date_end):
                        res_obj = {}
                        res_obj['name'] = obj.name + " (" + obj.get_guidelines_str() + ")"
                        tasks = event_obj.search([('attendees_group_ids', 'in', org_group.id),
                                                  ('objective_id', '=', obj.id),
                                                  ('stop', '>=', date_start),
                                                  ('start', '<=', date_end), ('parent_id', '=', False)])

                        parent_list = self._format_task_annual_plan(tasks, timezone)
                        task_list_obj = []
                        count = 1
                        for task in parent_list:
                            task['no'] = str(count)
                            task_list_obj.append(task)
                            self._search_assurance_annual_plan(org_group.id, task, task_list_obj, date_start, date_end, timezone)
                            count += 1

                        res_obj['task_list'] = task_list_obj
                        category_list.append(res_obj)

        objectives_search = self.env['l10n_cu_calendar.objective_task'].search([('group_id', '=', data['group_id']),
                                                                                ('period_id', '=', data['period_id'])])
        objectives_list = list(set([obj['name'] for obj in objectives_search]))
        objectives = [{'name': obj} for obj in objectives_list]

        gruop_plan_res[0]['name'] = org_group.name.upper()
        gruop_plan_res[0]['approved_by'] = data['approved_by'] if data['approved_by'] else org_group.partner_id.name
        gruop_plan_res[0]['approved_function'] = data['approved_function'] if data[
            'approved_by'] else org_group.partner_id.function
        gruop_plan_res[0]['group_chief'] = data['elaborated_by'] if data[
            'elaborated_by'] else org_group.partner_id.name
        gruop_plan_res[0]['group_chief_job'] = data['elaborated_function'] if data[
            'elaborated_by'] else org_group.partner_id.function

        gruop_plan_res[0]['periodo'] = data['periodo']
        gruop_plan_res[0]['category_list'] = category_list
        gruop_plan_res[0]['objectives_list'] = objectives

        return gruop_plan_res

