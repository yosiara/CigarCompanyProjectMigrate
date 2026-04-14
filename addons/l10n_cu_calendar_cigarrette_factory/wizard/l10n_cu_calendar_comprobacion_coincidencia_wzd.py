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

from odoo import models, fields, api, _, tools
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
import pytz


class PrintCalendarCompCoincid(models.TransientModel):
    _name = "l10n_cu_calendar.print_comp_coincid"

    # COLUMNS
    period_id = fields.Many2one('l10n_cu_period.period', string='Período', required=True)
    org_group_id = fields.Many2one('l10n_cu_calendar.org_group', string='Grupo Organizativo', required=True)
    # group_member_ids = fields.Many2many('res.partner', 'l10n_cu_calendar_org_group_partner_group_list', 'group_id',
    #                                     'partner_id', string='Miembros', required=True,
    #                                     domain="[('employee','=',True)]",related='org_group_id.partner_group_ids')
    group_member_ids = fields.Many2many('res.partner', 'l10n_cu_calendar_org_group_partner_group_list', 'group_id',
                                        'partner_id', string='Miembros')
    # -------

    @api.onchange('org_group_id')
    def _onchange_org_group_id(self):
        partners = []
        if self.org_group_id:
            # Aqui montar el domain para los partners del grupo organizativo
            for partner in self.org_group_id.partner_group_ids:
                partners.append(partner.id)

        domain = "[('id','in'," + str(partners) + ")]"
        return {'domain': {'group_member_ids': domain}}

    def invert_date(self, aux_date):
        return aux_date[8:10] + "/" + aux_date[5:7] + "/" + aux_date[0:4]

    @api.multi
    def print_comp_coincid(self):
        data = {}
        data['periodo'] = self.period_id.name

        org_groups = self.env['l10n_cu_calendar.org_group'].search([('id', '=', self.org_group_id.id)])
        partners_list = []
        partners_list_ids = []
        data['lista'] = []
        partner_tarea = []

        if self.group_member_ids:
            for partner in self.group_member_ids:
                if partner.id not in partners_list_ids:
                    partners_list_ids.append(partner.id)
                    partners_list.append(partner)
        else:
            for partner in self.org_group_id.partner_group_ids:
                if partner.id not in partners_list_ids:
                    partners_list_ids.append(partner.id)
                    partners_list.append(partner)
        #
        # for group in org_groups:
        #     for member in group.partner_group_ids:
        #         if member.id not in partners_list_ids:
        #             partners_list_ids.append(member.id)
        #             partners_list.append(member)

        # Buscar todas las tareas del periodo.
        tareas = self.env['calendar.event'].search([('start', '>=', self.period_id.date_start + ' 00:00:01'),
                                                    ('start', '<=', self.period_id.date_stop + ' 23:59:59')])

        for partner in partners_list:
            for task in tareas:
                if task.allday:
                    date_start = task.start_date + ' 00:00:00'
                    date_end = task.stop_date + ' 23:59:59'
                else:
                    tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
                    date_start_aux = fields.Datetime.from_string(task.start_datetime)
                    date_start = tz.localize(date_start_aux).astimezone(pytz.utc)
                    date_start = fields.Datetime.to_string(date_start)
                    date_end_aux = fields.Datetime.from_string(task.stop_datetime)
                    date_end = tz.localize(date_start_aux).astimezone(pytz.utc)
                    date_end = fields.Datetime.to_string(date_end)

                flag = False
                domain_search = [('start', '<=', date_end), ('stop', '>=', date_end)]
                if isinstance(task.id, int):
                    domain_search.append(('id', '!=', task.id))
                meetings_object = self.env['calendar.event'].with_context(mymeetings=False).search(domain_search)

                if len(meetings_object) > 0:
                    ids_object = []
                    for ids in meetings_object:
                        if partner.id in ids.partner_ids._ids:
                            if ids.id not in ids_object:
                                ids_object.append(ids.id)
                            flag = True

                    if flag:
                        data['lista'].append({'partner': partner.name,
                                              'actividad': task.name,
                                              'desde': task.start})

                if not flag:
                    domain_search = [('start', '<=', date_start), ('stop', '>=', date_start)]
                    if isinstance(task.id, int):
                        domain_search.append(('id', '!=', task.id))
                    meetings_object = self.env['calendar.event'].with_context(mymeetings=False).search(domain_search)

                    if len(meetings_object) > 0:
                        ids_object = []
                        for ids in meetings_object:
                            if partner.id in ids.partner_ids._ids:
                                if ids.id not in ids_object:
                                    ids_object.append(ids.id)
                                flag = True

                        if flag:
                            data['lista'].append({'partner': partner.name,
                                                  'actividad': task.name,
                                                  'desde': task.start})
                if not flag:
                    domain_search = [('start', '>=', date_start), ('stop', '<=', date_end)]
                    if isinstance(task.id, int):
                        domain_search.append(('id', '!=', task.id))
                    meetings_object = self.env['calendar.event'].with_context(mymeetings=False).search(domain_search)

                    if len(meetings_object) > 0:
                        ids_object = []
                        for ids in meetings_object:
                            if partner.id in ids.partner_ids._ids:
                                if ids.id not in ids_object:
                                    ids_object.append(ids.id)
                                flag = True

                        if flag:
                            data['lista'].append({'partner': partner.name,
                                                  'actividad': task.name,
                                                  'desde': task.start})

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_calendar.comp_coincid_doc_report',
                'datas': data,
            }

