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

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from calendar import Calendar
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz

_logger = logging.getLogger(__name__)


month_dic = {'01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril', '05': 'mayo', '06': 'junio',
             '07': 'julio', '08': 'agosto', '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'}


class CalendarPrintIndividualPlan(models.TransientModel):
    _name = "calendar_turei.print_individual_plan"
    _description = "calendar_turei.print_individual_plan"

    # COLUMNS
    date_start = fields.Date(related='period_id.date_start', store=True, readonly=True)
    date_end = fields.Date(related='period_id.date_end', store=True, readonly=True)
    period_id = fields.Many2one('calendar_turei.periods', string='Período', required=True)
    type = fields.Selection([('plan', 'Plan')], 'Type', required=True,
                            default='plan')
    text = fields.Html('Cualitative Resume', default="")
    confirmed = fields.Boolean('Confirmed', default=True)
    name = fields.Char('File Name', readonly=True)
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('print', 'Print')],  # choose print or get the ics file
                             default='print')
    format = fields.Selection([('pdf', 'PDF')], 'Output Format', required=True, default='pdf')

    # -------
    # imprimir Tareas del Plan
    def print_individual_plan(self):
        data = {}
        data['date_start'] = fields.Date().to_string(self.date_start)
        data['date_end'] = fields.Date().to_string(self.date_end)
        data['periodo'] = self.period_id.name
        data['text'] = self.text
        data['employee_id'] = self.env['hr.employee'].search([('id', '=', self._context['active_id'])]).id
        user_id = self._context['uid']
        employee = self.sudo().env['hr.employee'].browse(data['employee_id'])
        partner_id = employee.user_id.partner_id.id
        event_obj = self.env['calendar.event']
        if self.type == 'plan':
            if self.confirmed:
                # se aprueban las tareas y las tareas recurrentes deben convertirse en tareas fisicas o no virtuales
                # se buscan la tareas recurrentes del grupo en el periodo del año actual
                # se fija el rango de fecha al año actual para las tareas recurrentes
                fecha_start = datetime.strptime(data['date_start'], DEFAULT_SERVER_DATE_FORMAT)
                fecha_stop = datetime.strptime(data['date_end'], DEFAULT_SERVER_DATE_FORMAT)

            report_obj = self.env['ir.actions.report']
            data['enable_editor'] = 0
            report = report_obj._get_report_from_name('calendar_turei.report_individual_plan')
            test = self.env.context.get('active_ids', [])
            model = self.env.context.get('active_model')

            event_obj = self.env['calendar.event']
            date_start = data['date_start']
            date_end = data['date_end']
            employee = self.env['hr.employee'].browse(data['employee_id'])
            partner_id = employee.user_id.partner_id.id
            # IMPORTANTE!!
            event_list = []  # esta lista se utiliza para almacenar los dias con el listado de tareas
            # se toman las tareas que no son recurrentes en el rango de fechas
            event_ids = event_obj.search(
                [('partner_ids', 'in', partner_id), ('start', '>=', date_start), ('start', '<=', date_end),
                 ('recurrency', '=', False)])
            for e in event_ids:
                # take the user timezone
                timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                startdate = pytz.UTC.localize(fields.Datetime.from_string(e.start))  # Add "+hh:mm" timezone
                stoptdate = pytz.UTC.localize(fields.Datetime.from_string(e.stop))  # Add "+hh:mm" timezone
                # Convert the start date to saved timezone (or context tz) as it'll
                # define the correct hour/day asked by the user to repeat for recurrence.
                start = startdate.astimezone(timezone)  # transform "+hh:mm" timezone
                stop = stoptdate.astimezone(timezone)  # transform "+hh:mm" timezone
                start = fields.Datetime.to_string(start)  # convert to string
                stop = fields.Datetime.to_string(stop)  # convert to string

                res = {}
                res['name'] = e.short_name
                res['start'] = str(start)[:10]
                res['stop'] = str(stop)[:10]
                res['hour_start'] = 'T/D' if e.allday else str(start)[11:][:5]
                res['local'] = e.location
                res['priority'] = e.priority
                res['orderby'] = str(start)[:10][8:] + str(start)[11:][:2]
                event_list.append(res)

            # se buscan la tareas recurrentes
            # se tiene que buscar las tareas recurrentes del empleado en el periodo del año actual
            # se fija el rango de fecha al año actual para las tareas recurrentes
            fecha = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
            year_first_day = str(fecha.year) + '-01-01'
            year_last_day = str(fecha.year) + '-12-31'
            rec_event_ids = event_obj.search(
                [('partner_ids', 'in', partner_id), ('start', '>=', year_first_day), ('start', '<=', year_last_day),
                 ('recurrency', '=', True)])
            for e in rec_event_ids:
                event_start = str(e.start)[:10]
                if date_start <= event_start <= date_end:
                    # take the user timezone
                    timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                    startdate = pytz.UTC.localize(fields.Datetime.from_string(e.start))  # Add "+hh:mm" timezone
                    stoptdate = pytz.UTC.localize(fields.Datetime.from_string(e.stop))  # Add "+hh:mm" timezone
                    # Convert the start date to saved timezone (or context tz) as it'll
                    # define the correct hour/day asked by the user to repeat for recurrence.
                    start = startdate.astimezone(timezone)  # transform "+hh:mm" timezone
                    stop = stoptdate.astimezone(timezone)  # transform "+hh:mm" timezone
                    start = fields.Datetime.to_string(start)  # convert to string
                    stop = fields.Datetime.to_string(stop)  # convert to string

                    res = {}
                    res['name'] = e.short_name
                    # res['name'] = e.name
                    res['start'] = str(start)[:10]
                    res['stop'] = str(stop)[:10]
                    res['hour_start'] = 'T/D' if e.allday else str(start)[11:][:5]
                    res['local'] = e.location
                    # res['local'] = e.local_id.name
                    res['priority'] = e.priority
                    res['orderby'] = str(start)[:10][8:] + str(start)[11:][:2]
                    event_list.append(res)

            # event_list = Listado de las tareas para armar el reporte

            indv_plan_res = [
                {'id': '', 'name': '', 'job': '', 'manager_name': '', 'manager_job': '', 'mes': '', 'anno': '',
                 'main_task_list': [], 'login': '', 'calendar': []}]

            # INCIALIZAMOS
            indv_plan_res[0]['name'] = employee.name
            indv_plan_res[0]['job'] = employee.job_id.name
            indv_plan_res[0]['manager_name'] = employee.parent_id.name
            indv_plan_res[0]['manager_job'] = employee.parent_id.job_id.name
            indv_plan_res[0]['area'] = employee.department_id.name

            c = Calendar()

            # buscar la fecha de inicio de periodo para tomar el mes
            fecha = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)

            # actualmenete se toma el mes de la fecha de inicio del periodo
            # TODO: hacer esto dinamico para que se tome el rango definido en el periodo
            indv_plan_res[0]['mes'] = data['periodo']  # indv_plan.period_id.name

            # ordenar las taras antes de organizarlas
            event_list.sort(key=lambda x: x['orderby'])
            # organizar las tareas en el calendario

            calendario = []  # Lista de semanas
            main_task_list = []  # Lista de tareas principales
            for week in c.monthdayscalendar(fecha.year, fecha.month):
                semana = []
                for d in week:
                    dia = {'dia': d, 'task': []}
                    if d:
                        t_list = []
                        date_time_am = str(fecha.year) + '-' + str(fecha.month) + '-' + str(d)
                        date_time_am = datetime.strptime(date_time_am, DEFAULT_SERVER_DATE_FORMAT)
                        date_time_am = date_time_am.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        for event in event_list:
                            if event['start'] <= date_time_am <= event['stop']:
                                t_list.append(event)
                            if event['priority'] == '2':
                                if event['name'] not in main_task_list:
                                    main_task_list.append(event['name'])

                        dia = {'dia': d, 'task': t_list}
                    semana.append(dia)
                calendario.append(semana)
            # #print calendario
            indv_plan_res[0]['calendar'] = calendario
            indv_plan_res[0]['main_task_list'] = main_task_list

            if self.format == 'pdf':
                data['docs'] = indv_plan_res
                return self.env.ref('calendar_turei.action_report_individual_plan').report_action([], data=data)

