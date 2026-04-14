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
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz
_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import pkg_resources

resp_dic = {'nokey': _ ( 'Debe solicitar una clave de registro. Póngase en contacto con el centro de soporte técnico, a través de la dirección de correo comercial.holguin@desoft.cu para obtener una nueva.' ),
            'invalidkey': _ ( 'Está utilizando una clave no válida. Póngase en contacto con el centro de soporte técnico, a través de la dirección de correo comercial.holguin@desoft.cu para obtener una nueva.' ),
            'expkey': _ ( 'Está utilizando una clave caducada. Póngase en contacto con el centro de soporte técnico, a través de la dirección de correo comercial.holguin@desoft.cu para obtener una nueva.' )}


class CalendarPrintGroupPlan(models.TransientModel):
    _name = "l10n_cu_calendar.print_group_plan"

    # COLUMNS
    date_start = fields.Date('Date Start',related='period_id.date_start', readonly=True)
    date_start_custom = fields.Date('Date Start')
    date_end = fields.Date('Date End', related='period_id.date_stop', readonly=True)
    date_end_custom = fields.Date('Date End')
    period_id = fields.Many2one('l10n_cu_period.period', string='Period')
    custom_period = fields.Boolean(string='Custom Period', default=False, required=False)
    text = fields.Html('Cualitative Resume')
    type = fields.Selection([('monthly', 'Monthly organization work plan'), ('annual', 'Annual activities plan'),
                             ('resume_annual', 'Annual accomplish resume'),
                             ('resume_monthly', 'Monthly accomplish resume'), ('detail', 'Detail report')],
                            'Type', required=True, default='monthly')
    confirmed = fields.Boolean('Confirmed', default=False)
    approved_by = fields.Many2one('res.partner', string='Approved By')
    elaborated_by = fields.Many2one('res.partner', string='Elaborated By')
    behave = fields.Boolean(string='Specify Authors', default=False)
    format = fields.Selection([('pdf', 'PDF'), ('docx', 'DOCX')], 'Output Format', required=True, default='pdf')

    # -------

    def _get_children(self, list, parent_id):
        task_category = self.env['l10n_cu_calendar.task_category']
        for catg in task_category.search([('parent_id', '=', parent_id)]):
            list.append(catg)
            self._get_children(list, catg.id)

    @api.onchange('type')
    def onchange_type(self):
        for res in self:
            value = {'domain': {}, 'value': {}}
            if res.type in ('monthly', 'resume_monthly', 'detail'):
                value['domain']['period_id'] = "[('annual','=',False)]"
                value['value']['period_id'] = False
            else:
                value['domain']['period_id'] = "[('annual','=',True)]"
                value['value']['period_id'] = False
                value['value']['custom_period'] = False
        return value

    @api.multi
    def print_group_plan(self):

        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_calendar')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        data = {}

        data['monthly'] = self.type in ('monthly', 'resume_monthly', 'detail')
        data['text'] = self.text
        data['date_start'] = self.date_start if not self.custom_period else self.date_start_custom
        data['approved_by'] = self.approved_by.name
        data['approved_function'] = self.approved_by.function
        data['elaborated_by'] = self.elaborated_by.name
        data['elaborated_function'] = self.elaborated_by.function
        data['date_end'] = self.date_end if not self.custom_period else self.date_end_custom
        data['periodo'] = self.period_id.name.upper() if self.period_id else ''
        data['period_id'] = self.period_id.id if self.custom_period else False
        data['group_id'] = self.env['l10n_cu_calendar.org_group'].search([('id', '=', self._context['active_id'])]).id

        event_obj = self.env['calendar.event']
        if self.type == 'monthly':
            if self.confirmed:
                # se aprueban las tareas y las tareas recurrentes deben convertirse en tareas fisicas o no virtuales
                # se buscan la tareas recurrentes del grupo en el periodo del año actual
                # se fija el rango de fecha al año actual para las tareas recurrentes
                fecha_start = datetime.strptime(data['date_start'], DEFAULT_SERVER_DATE_FORMAT)
                fecha_stop = datetime.strptime(data['date_end'], DEFAULT_SERVER_DATE_FORMAT)
                rec_event_ids = event_obj.search(
                    [('attendees_group_ids', 'in', data['group_id']), ('stop', '>=', fecha_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('start', '<=', fecha_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
                for e in rec_event_ids:
                    if e.recurrency:
                        e.detach_recurring_event()
                event_ids = event_obj.search(
                    [('state', '=', 'draft'), ('attendees_group_ids', 'in', data['group_id']), ('recurrency', '=', False), ('stop', '>=', fecha_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                      ('start', '<=', fecha_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
                if event_ids:
                    event_ids.write({'state': 'open'})

            data['enable_editor'] = 0

            if self.env.user.company_id.include_obj_cat_monthly_plan:

                gruop_plan_res = self.env['l10n_cu_calendar.report_utils']._compute_obj_cat_monthly_plan(data)

                if self.format == 'pdf':
                    return self.env['report'].get_action(
                        self, 'l10n_cu_calendar.report_group_plan_category',
                        data={'docs': gruop_plan_res}
                    )
                else:
                    path = pkg_resources.resource_filename(
                        "odoo.addons.l10n_cu_calendar",
                        "static/src/img/dummy_logo.png",
                    )
                    gruop_plan_res[0]['replace_logo'] = {'src': 'path', 'data': path}
                    report_name = 'l10n_cu_calendar.monthly_group_plan_category_report_docx' if not self.env.user.company_id.show_observation_column else 'l10n_cu_calendar.monthly_group_plan_category_obs_report_docx'
                    return {
                        'type': 'ir.actions.report.xml',
                        'report_name': report_name,
                        'datas': gruop_plan_res[0]
                    }
            else:
                gruop_plan_res = self.env['l10n_cu_calendar.report_utils']._compute_monthly_plan(data)

                if self.format == 'pdf':
                    return self.env['report'].get_action(self, 'l10n_cu_calendar.report_group_plan', data={'docs': gruop_plan_res})
                else:
                    path = pkg_resources.resource_filename(
                        "odoo.addons.l10n_cu_calendar",
                        "static/src/img/dummy_logo.png",
                    )
                    gruop_plan_res[0]['replace_logo'] = { 'src': 'path', 'data': path }
                    report_name = 'l10n_cu_calendar.monthly_group_plan_docx' if not self.env.user.company_id.show_observation_column else 'l10n_cu_calendar.monthly_group_plan_obs_docx'
                    return {
                        'type': 'ir.actions.report.xml',
                        'report_name': report_name,
                        'datas': gruop_plan_res[0]
                    }
        elif self.type == 'annual':

            gruop_plan_res = self.env['l10n_cu_calendar.report_utils']._compute_annual_plan(data)

            if self.format == 'pdf':
                return self.env['report'].get_action(self, 'l10n_cu_calendar.report_anual_group_plan', data={'docs': gruop_plan_res})
            else:
                path = pkg_resources.resource_filename(
                    "odoo.addons.l10n_cu_calendar",
                    "static/src/img/dummy_logo.png",
                )
                gruop_plan_res[0]['replace_logo'] = { 'src': 'path', 'data': path }
                report_name = 'l10n_cu_calendar.annual_group_plan_docx' if not self.env.user.company_id.show_annual_observation_column else 'l10n_cu_calendar.annual_group_plan_obs_docx'
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': report_name,
                    'datas': gruop_plan_res[0]
                }
        elif self.type == 'detail':
            org_group = self.env['l10n_cu_calendar.org_group'].browse(data['group_id'])
            group_plan_res = [{'id': '', 'name': '', 'mes': '', 'year': '', 'period': '',
                               'group_chief': org_group.partner_id.name if org_group.partner_id else '',
                               'group_chief_job': org_group.partner_id.function if org_group.partner_id else ''}]

            # se toman las tareas que no son recurrentes en el rango de fechas
            year_end = data['date_end'][0:4] + '-12-31'
            event_ids = event_obj.search([('attendees_group_ids', 'in', org_group.id), ('recurrency', '=', False),
                                          ('start', '>=', data['date_start']), ('start', '<=', year_end)])
            # take the user timezone
            timezone = pytz.timezone(self._context.get('tz') or 'UTC')
            modified_task_list = []
            modified_ids = []
            for e in event_ids:
                res = {}
                res['name'] = e.name
                res['date'] = ''
                res['new_date'] = ''
                res['local'] = e.local_id.name
                res['directed_for'] = e.directed_by_job
                res['participants_char'] = e.participants_char()
                res['category_id'] = e.category_id.id
                res['objective_id'] = e.objective_id.id
                modified = False
                list_trace_field = ['start_date', 'start_datetime']  # campos a trace
                datetime_list_old = {}  # lista pra guardar las veces que fue modificada la fecha/hora de la tarea
                datetime_list_new = {}  # lista pra guardar las veces que fue modificada la fecha/hora de la tarea
                messages = self.env['mail.message'].search([('model', '=', 'calendar.event'), ('res_id', '=', e.id)], order='id asc')
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
                                if not datetime_list_old and trace.old_value_datetime and data['date_start'] <= trace.old_value_datetime <= data['date_end']:
                                    datetime_list_old = {'value': trace.old_value_datetime, 'field': trace.field}
                                    modified = True
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

                    res['date'] = old_value_datetime[:10][8:] + '/' + old_value_datetime[:10][5:7] + '/' + old_value_datetime[:10][0:4] + ', ' + old_hour
                    res['new_date'] = new_value_datetime[:10][8:] + '/' + new_value_datetime[:10][5:7] + '/' + new_value_datetime[:10][0:4] + ', ' + new_hour

                if modified:
                    if self.env.user.company_id.tasks_postponed_only:
                        if new_value_datetime and data['date_end'] + ' 23:59:59' < new_value_datetime:
                            modified_task_list.append(res)
                            modified_ids.append(e.id)
                    else:
                        modified_task_list.append(res)
                        modified_ids.append(e.id)

            global_list = []
            for catg in self.env['l10n_cu_calendar.task_category'].search([('parent_id', '=', False)]):
                global_list.append(catg)
                self._get_children(global_list, catg.id)

            category_list = []
            if modified_ids:
                for catg in global_list:
                    if catg.has_task(group_id=org_group.id, date_start=data['date_start'], date_end=data['date_end'], ids=modified_ids):
                        res = {'id': catg.id, 'name': catg.name, 'task_list': []}
                        task_list = []

                        for mt in modified_task_list:
                            if mt['category_id'] == catg.id and not mt['objective_id']:
                                task_list.append(mt)

                        res['task_list'] = task_list
                        category_list.append(res)

                        for obj in catg.objective_ids:
                            if obj.has_task(group_id=org_group.id, date_start=data['date_start'], date_end=data['date_end'], ids=modified_ids):
                                res_obj = {'name': obj.name + " (" + obj.get_guidelines_str() + ")"}
                                task_list_obj = []
                                for mt in modified_task_list:
                                    if mt['category_id'] == catg.id and mt['objective_id'] == obj.id:
                                        task_list_obj.append(mt)

                                res_obj['task_list'] = task_list_obj
                                category_list.append(res_obj)

            group_plan_res[0]['monthly'] = data['monthly']
            group_plan_res[0]['name'] = org_group.name.upper()
            group_plan_res[0]['period'] = data['periodo']
            group_plan_res[0]['category_list'] = category_list
            group_plan_res[0]['modified_task_list'] = modified_task_list

            if self.format == 'pdf':
                if self.env.user.company_id.include_obj_cat_monthly_plan:
                    return self.env['report'].get_action(
                        self, 'l10n_cu_calendar.report_detail_report',
                        data={'docs': group_plan_res}
                    )
                else:
                    return self.env['report'].get_action(
                        self, 'l10n_cu_calendar.report_detail_no_categ_report',
                        data={'docs': group_plan_res}
                    )
            else:
                path = pkg_resources.resource_filename(
                    "odoo.addons.l10n_cu_calendar",
                    "static/src/img/dummy_logo.png",
                )
                group_plan_res[0]['replace_logo'] = {'src': 'path', 'data': path}
                if self.env.user.company_id.include_obj_cat_monthly_plan:
                    return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'l10n_cu_calendar.detail_report_docx',
                        'datas': group_plan_res[0]
                    }
                else:
                    return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'l10n_cu_calendar.detail_no_categ_report_docx',
                        'datas': group_plan_res[0]
                    }
        else:
            report_data = self.env['l10n_cu_calendar.report_utils']._compute_group_resume_values(data)
            if self.format == 'pdf':
                return self.env['report'].get_action(self, 'l10n_cu_calendar.report_group_resume_plan', data={'docs': report_data})
            else:
                path = pkg_resources.resource_filename(
                    "odoo.addons.l10n_cu_calendar",
                    "static/src/img/dummy_logo.png",
                )
                report_data[0]['replace_logo'] = {'src': 'path', 'data': path}
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_calendar.group_plan_resume_docx',
                    'datas': report_data[0]
                }

