# -*- coding: utf-8 -*-
import logging
from calendar import Calendar
from datetime import date, datetime, timedelta

import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

FALLBACK_APPROVER_PARAM = 'calendar_turei.fallback_approver_name'
FALLBACK_APPROVER_JOB_PARAM = 'calendar_turei.fallback_approver_job'


class PrintIndividualPlan(models.TransientModel):
    _name = 'calendar_turei.print_individual_plan'
    _description = 'Print Individual Plan Wizard'

    def _previous_month_range(self):
        """Devuelve (primer_día_mes_anterior, último_día_mes_anterior) como date."""
        first_this_month = date.today().replace(day=1)
        last_prev_month = first_this_month - timedelta(days=1)
        first_prev_month = last_prev_month.replace(day=1)
        return first_prev_month, last_prev_month

    def _default_period_id(self):
        first_prev, last_prev = self._previous_month_range()
        return self.env['calendar_turei.periods'].search([
            ('anual', '=', False),
            ('start_date', '<=', fields.Date.to_string(first_prev)),
            ('end_date',   '>=', fields.Date.to_string(last_prev)),
        ], limit=1, order='start_date desc')

    period_id = fields.Many2one(
        'calendar_turei.periods', string='Period *', 
        required=True, default=_default_period_id, 
    )
    start_date = fields.Date(related='period_id.start_date', store=True, readonly=True)
    end_date = fields.Date(related='period_id.end_date', store=True, readonly=True)

    type = fields.Selection(
        selection=[('individual', 'Individual'), ('company', 'Company')],
        string='Type *', required=True, default='individual',
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        default=lambda self: self.env.user.employee_id, 
        help='Leave empty to print your own plan.',
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
    )

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------
    def print_individual_plan(self):
        self.ensure_one()

        start_date = fields.Date.to_string(self.start_date)
        end_date = fields.Date.to_string(self.end_date)

        if self.type == 'individual':
            partner, header = self._build_employee_header()
        else:
            partner, header = self._build_company_header()

        events = self._collect_events(partner.id, start_date, end_date)
        calendar, main_tasks = self._build_calendar(events, start_date)
        year = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).year

        doc = dict(header)
        doc.update({
            'month': self.period_id.name or '',
            'year': year,
            'report_title': (
                _('Company Work Plan') if self.type == 'company'
                else _('Individual Work Plan')
            ),
            'main_task_list': main_tasks,
            'login': '',
            'calendar': calendar,
        })

        data = {
            'start_date': start_date,
            'end_date': end_date,
            'is_company': self.type == 'company',
            'docs': [doc],
        }

        return self.env.ref(
            'calendar_turei.action_report_individual_plan'
        ).report_action([], data=data)

    # ------------------------------------------------------------------
    # Cabeceras
    # ------------------------------------------------------------------
    def _build_employee_header(self):
        employee = self.employee_id or self.env.user.employee_id
        if not employee:
            raise UserError(_('The current user is not linked to any employee.'))
        if not employee.work_contact_id:
            raise UserError(_('The employee has no associated work contact.'))

        manager_name, manager_job = self._resolve_approver(employee)

        return employee.work_contact_id, {
            'id': employee.id,
            'name': employee.name or '',
            'job': employee.job_id.name or '',
            'manager_name': manager_name,
            'manager_job': manager_job,
            'area': employee.department_id.name or '',
        }

    def _build_company_header(self):
        company = self.company_id or self.env.company
        partner = company.partner_id
        if not partner:
            raise UserError(_('The selected company has no associated partner.'))

        fallback_name = self._get_param(FALLBACK_APPROVER_PARAM, company.name)
        fallback_job = self._get_param(FALLBACK_APPROVER_JOB_PARAM, '')

        return partner, {
            'id': False,
            'name': company.name or '',
            'job': '',
            'manager_name': fallback_name,
            'manager_job': fallback_job,
            'area': company.name or '',
        }

    # ------------------------------------------------------------------
    # Resolución del "Aprobado por"
    # ------------------------------------------------------------------
    def _resolve_approver(self, employee):
        """
        Cadena de fallback:
          1. Manager directo (employee.parent_id)
          2. Parámetro de sistema calendar_turei.fallback_approver_name
          3. Nombre de la compañía
        """
        if employee.parent_id:
            return (
                employee.parent_id.name or '',
                employee.parent_id.job_id.name or '',
            )

        company = employee.company_id or self.env.company
        return (
            self._get_param(FALLBACK_APPROVER_PARAM, company.name),
            self._get_param(FALLBACK_APPROVER_JOB_PARAM, ''),
        )

    def _get_param(self, key, default=''):
        return self.env['ir.config_parameter'].sudo().get_param(key, default=default)

    # ------------------------------------------------------------------
    # Recolección de eventos
    # ------------------------------------------------------------------
    def _collect_events(self, partner_id, start_date, end_date):
        event_obj = self.env['calendar.event']
        events = []

        # No recurrentes dentro del período
        for e in event_obj.search([
            ('partner_ids', 'in', partner_id),
            ('start', '>=', start_date),
            ('start', '<=', end_date),
            ('recurrency', '=', False),
        ]):
            events.append(self._prepare_event(e))

        # Recurrentes dentro del año (con filtro posterior por rango)
        year = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).year
        for e in event_obj.search([
            ('partner_ids', 'in', partner_id),
            ('start', '>=', '%04d-01-01' % year),
            ('start', '<=', '%04d-12-31' % year),
            ('recurrency', '=', True),
        ]):
            if start_date <= str(e.start)[:10] <= end_date:
                events.append(self._prepare_event(e))

        events.sort(key=lambda x: x['orderby'])
        return events

    # ------------------------------------------------------------------
    # Construcción del calendario
    # ------------------------------------------------------------------
    def _build_calendar(self, events, start_date):
        fecha = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        calendar = []
        main_tasks = []

        for w in Calendar().monthdayscalendar(fecha.year, fecha.month):
            week = []
            for d in w:
                day = {'day': d, 'task': []}
                if d:
                    date_str = '%04d-%02d-%02d' % (fecha.year, fecha.month, d)
                    t_list = [e for e in events if e['start'] <= date_str <= e['stop']]
                    for e in t_list:
                        if e['priority'] == '2' and e['name'] not in main_tasks:
                            main_tasks.append(e['name'])
                    day = {'day': d, 'task': t_list}
                week.append(day)
            calendar.append(week)

        return calendar, main_tasks

    # ------------------------------------------------------------------
    # Normalización de evento
    # ------------------------------------------------------------------
    def _prepare_event(self, event):
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
            'orderby': start[8:10] + start[11:13],
        }