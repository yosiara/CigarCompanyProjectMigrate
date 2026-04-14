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
from odoo import models, fields, api, _, SUPERUSER_ID
from datetime import datetime,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class CmiExecuteTransformations(models.TransientModel):
    _name = "cmi.execute_transformations_wzd"

    date = fields.Date(string='Date', required=True)

    @api.multi
    def execute(self):
        date = datetime.strptime(self.date, DEFAULT_SERVER_DATE_FORMAT)
        self.env['cmi.indicator']._cron_execute_transformations(self.date)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }