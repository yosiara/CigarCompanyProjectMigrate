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

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import models, fields, api
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.addons.calendar.models.calendar import calendar_id2real_id


class CalendarToNextYear(models.TransientModel):
    _name = "l10n_cu_calendar.to_next_year"

    # COLUMNS
    previous_period_id = fields.Many2one('l10n_cu_period.period', string='Previous period', required=True, domain=[('annual', '=', True)])
    next_period_id = fields.Many2one('l10n_cu_period.period', string='Next period', required=True, domain=[('annual', '=', True)])
    # -------

    @api.onchange('previous_period_id')
    def onchange_previous_period_id(self):
        if self.previous_period_id.id:
            return {'domain': {'next_period_id': "[('id','!='," + str(self.previous_period_id.id) + "),('annual','=',True)]"}}

    @api.onchange('next_period_id')
    def onchange_next_period_id(self):
        if self.next_period_id.id:
            return {'domain': {'previous_period_id': "[('id','!='," + str(self.next_period_id.id) + "),('annual','=',True)]"}}

    @api.multi
    def to_next_year(self):
        if int(str(self.next_period_id.date_start)[0:4]) <= int(str(self.previous_period_id.date_start)[0:4]):
            raise ValidationError(_('The next period must be more actual than the previous period!'))
        else:
            event_obj = self.env['calendar.event']
            events = event_obj.search([('repeat_other_year', '=', True), ('active', '=', True),  #('recurrent_id', '=', 0),
                                       ('start', '>=', self.previous_period_id.date_start),
                                       ('start', '<=', self.previous_period_id.date_stop)])

            id_list = []
            for e in events:
                if e.id and isinstance(e.id, (basestring)):
                    real_id = calendar_id2real_id(e.id)
                    e = event_obj.browse(real_id)

                if e.recurrent_id > 0:
                    e = event_obj.browse(e.recurrent_id)

                if e.id not in id_list:
                    repeat_events = event_obj.search([('repeat_id', '=', e.id),
                                                      ('start', '>=', self.next_period_id.date_start),
                                                      ('stop', '<=', self.next_period_id.date_stop)])
                    if len(repeat_events) > 0:
                        id_list.append(e.id)
                        continue

                    start = datetime(int(str(self.next_period_id.date_start)[0:4]), int(str(e.start)[5:7]),
                                     int(str(e.start)[8:10]), int(str(e.start)[11:13]), int(str(e.start)[14:16]))
                    stop = datetime(int(str(self.next_period_id.date_start)[0:4]), int(str(e.stop)[5:7]),
                                    int(str(e.stop)[8:10]), int(str(e.stop)[11:13]), int(str(e.stop)[14:16]))

                    if e.recurrency and e.final_date:
                        final_date = date(int(str(self.next_period_id.date_start)[0:4]), int(str(e.final_date)[5:7]), int(str(e.final_date)[8:10]))
                    else:
                        final_date = None

                    if e.allday:
                        display_start = datetime(int(str(self.next_period_id.date_start)[0:4]),
                                                 int(str(e.display_start)[5:7]), int(str(e.display_start)[8:10]))
                        start_date = date(int(str(self.next_period_id.date_start)[0:4]), int(str(e.start_date)[5:7]),
                                          int(str(e.start_date)[8:10]))
                        stop_date = datetime(int(str(self.next_period_id.date_start)[0:4]), int(str(e.stop_date)[5:7]),
                                             int(str(e.stop_date)[8:10]))
                    else:
                        display_start = datetime(int(str(self.next_period_id.date_start)[0:4]),
                                                 int(str(e.display_start)[5:7]), int(str(e.display_start)[8:10]),
                                                 int(str(e.display_start)[11:13]), int(str(e.display_start)[14:16]))
                        start_date = e.start_date
                        stop_date = e.stop_date

                    start_date = start_date.strftime('%Y-%m-%d')
                    e.copy({'start': start, 'stop': stop, 'final_date': final_date, 'display_start': display_start,
                            'start_date': start_date, 'stop_date': stop_date, 'repeat_id': e.id})
                    id_list.append(e.id)

            return True
