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
from odoo.tools.translate import _


class CalendarAttendeeNotDoneAllWzd(models.TransientModel):
    _name = "l10n_cu_calendar.attendee_not_done_all_wzd"

    # COLUMNS
    # -------

    @api.multi
    def execute(self):
        if self._context.get('active_ids'):
            attendees = self.env['calendar.attendee'].browse(self._context.get('active_ids'))
            attendees.task_not_done()
        return True
