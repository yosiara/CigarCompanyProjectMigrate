# -*- coding: utf-8 -*-
import logging
from datetime import datetime

import pytz
from calendar import Calendar

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class PrintIndividualPlan(models.TransientModel):
    _name = 'calendar_turei.print_individual_plan'
    _description = 'Print Individual Plan Wizard'

    period_id = fields.Many2one('calendar_turei.periods', string='Período', required=True)
    start_date = fields.Date(related='period_id.start_date', store=True, readonly=True)
    end_date = fields.Date(related='period_id.end_date', store=True, readonly=True)
    type = fields.Selection([('plan', 'Plan')], 'Tipo', required=True, default='plan')

    def print_individual_plan(self):
        self.ensure_one()

        # --- 1) Empleado del usuario actual ---
        employee = self.env.user.employee_id
        if not employee:
            raise UserError(_('The current user is not linked to any employee.'))
        if not employee.work_contact_id:
            raise UserError(_('The employee has no associated work contact.'))

        start_date = fields.Date.to_string(self.start_date)
        end_date = fields.Date.to_string(self.end_date)
        partner_id = employee.work_contact_id.id

        data = {
            'start_date': start_date,
            'end_date': end_date,
            'employee_id': employee.id,
        }

        if self.type != 'plan':
            return False

        event_obj = self.env['calendar.event']
        event_list = []

        # --- 2) Eventos NO recurrentes dentro del período ---
        event_ids = event_obj.search([
            ('partner_ids', 'in', partner_id),
            ('start', '>=', start_date),
            ('start', '<=', end_date),
            ('recurrency', '=', False),
        ])
        for e in event_ids:
            event_list.append(self._prepare_event(e))

        # --- 3) Eventos recurrentes dentro del año actual ---
        fecha = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        year_first_day = '%04d-01-01' % fecha.year
        year_last_day = '%04d-12-31' % fecha.year

        rec_event_ids = event_obj.search([
            ('partner_ids', 'in', partner_id),
            ('start', '>=', year_first_day),
            ('start', '<=', year_last_day),
            ('recurrency', '=', True),
        ])
        for e in rec_event_ids:
            event_start = str(e.start)[:10]
            if start_date <= event_start <= end_date:
                event_list.append(self._prepare_event(e))

        # --- 4) Ordenar y armar calendario ---
        event_list.sort(key=lambda x: x['orderby'])

        calendario = []
        main_task_list = []
        for week in Calendar().monthdayscalendar(fecha.year, fecha.month):
            semana = []
            for d in week:
                dia = {'dia': d, 'task': []}
                if d:
                    # ✅ Fechas con ceros a la izquierda (YYYY-MM-DD)
                    date_str = '%04d-%02d-%02d' % (fecha.year, fecha.month, d)
                    t_list = []
                    for event in event_list:
                        if event['start'] <= date_str <= event['stop']:
                            t_list.append(event)
                        if event['priority'] == '2' and event['name'] not in main_task_list:
                            main_task_list.append(event['name'])
                    dia = {'dia': d, 'task': t_list}
                semana.append(dia)
            calendario.append(semana)

        data['docs'] = [{
            'id': '',
            'name': employee.name or '',
            'job': employee.job_id.name or '',
            'manager_name': employee.parent_id.name or '',
            'manager_job': employee.parent_id.job_id.name or '',
            'area': employee.department_id.name or '',
            'mes': self.period_id.name or '',
            'anno': fecha.year,
            'main_task_list': main_task_list,
            'login': '',
            'calendar': calendario,
        }]

        return self.env.ref('calendar_turei.action_report_individual_plan').report_action([], data=data)

    def _prepare_event(self, event):
        """Normaliza un calendar.event a un dict listo para el reporte."""
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        start_utc = pytz.UTC.localize(fields.Datetime.from_string(event.start))
        stop_utc = pytz.UTC.localize(fields.Datetime.from_string(event.stop))
        start = fields.Datetime.to_string(start_utc.astimezone(timezone))
        stop = fields.Datetime.to_string(stop_utc.astimezone(timezone))
        return {
            'name': event.short_name or '',
            'start': start[:10],
            'stop': stop[:10],
            'hour_start': 'T/D' if event.allday else start[11:16],
            'local': event.location or '',
            'priority': event.priority,
            'orderby': start[8:10] + start[11:13],  # DD + HH para ordenar
        }