# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    Desoft. Holguín. Cuba.
#    Copyright (C) Desoft. Holguín. Cuba. <http://www.desoft.cu>.
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
from odoo import api
from odoo import fields, models
from odoo.http import root
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import *
from datetime import datetime


_logger = logging.getLogger(__name__)


class ir_sessions(models.Model):
    _name = 'ir.sessions'
    _description = "Sessions"

    user_id = fields.Many2one('res.users', 'User', ondelete='cascade', required=True)
    logged_in = fields.Boolean('Logged in', required=True, index=True)
    session_id = fields.Char('Session ID', size=100, required=True)
    last_use = fields.Datetime('Last Use')
    ip = fields.Char('Remote IP', size=15, required=True)
    type_session = fields.Selection(
        [
            ('standard', 'Standard'),
            ('movil', 'Movil')
        ], 'Session Type', required=True, default='standard')

    # scheduler function to validate users session
    def validate_sessions(self):
        delta = (fields.datetime.now() - relativedelta(hours=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        sessions = self.sudo().search([('last_use', '<=', delta), ('type_session', '=', 'standard'), ('logged_in', '=', True)])
        if sessions:
            sessions._close_session()
        return True

    @api.multi
    def _on_session_logout(self):
        cr = self.pool.cursor()
        # autocommit: our single update request will be performed atomically.
        # (In this way, there is no opportunity to have two transactions
        # interleaving their cr.execute()..cr.commit() calls and have one
        # of them rolled back due to a concurrent access.)
        cr.autocommit(True)

        for session in self:
            session.sudo().write({'logged_in': False})
        cr.commit()
        cr.close()
        return True

    @api.multi
    def _close_session(self):
        redirect = False
        for r in self:
            if r.user_id.id == self.env.user.id:
                redirect = True

            session = root.session_store.get(r.session_id)
            session.logout(keep_db=True, env=self.env)
        return redirect
