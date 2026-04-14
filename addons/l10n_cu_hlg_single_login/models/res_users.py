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
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from odoo.http import request
from odoo import api
from odoo import fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class res_users(models.Model):
    _inherit = 'res.users'

    session_ids = fields.One2many('ir.sessions', 'user_id', 'User Sessions')
    block_multiple_session = fields.Boolean('Block Multiple Sessions', default=True)

    @api.model
    def _check_session_validity(self, db, uid, passwd):
        if not request:
            return
        now = fields.datetime.now()
        session = request.session
        if session.db and session.uid:
            session_obj = request.env['ir.sessions']
            cr = self.pool.cursor()
            cr.autocommit(True)
            session_ids = session_obj.search([('session_id', '=', session.sid), ('logged_in', '=', True)])
            if session_ids:
                if request.httprequest.path[:5] == '/web/' or \
                        request.httprequest.path[:9] == '/im_chat/' or \
                        request.httprequest.path[:6] == '/ajax/':
                    for s in session_ids:
                        last_use = now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        cr.execute('UPDATE ir_sessions ' \
                                   'SET last_use=%s ' \
                                   'WHERE id= %s', (last_use, s.id))
                    cr.commit()
            else:
                session.logout(keep_db=True)
            cr.close()
        return True

    @classmethod
    def check(cls, db, uid, passwd):
        res = super(res_users, cls).check(db, uid, passwd)
        cr = cls.pool.cursor()
        self = api.Environment(cr, uid, {})[cls._name]
        cr.commit()
        cr.close()
        self.browse(uid)._check_session_validity(db, uid, passwd)
        return res

    @api.one
    def action_close_session(self):
        session_obj = request.env['ir.sessions']
        session_ids = session_obj.search([('user_id', '=', self.id), ('type_session', '=', 'standard'), ('logged_in', '=', True)])
        redirect = session_ids._close_session()
        if redirect:
            return werkzeug.utils.redirect(
                '/web/login?db=%s' %
                self.env.cr.dbname, 303)