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

import odoo
from odoo import SUPERUSER_ID
from odoo import fields, _
from odoo import http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

# from odoo import pooler

_logger = logging.getLogger(__name__)


def _get_request_ip():
    ip = request.httprequest.headers.environ['REMOTE_ADDR']
    if 'HTTP_X_FORWARDED_FOR' in request.httprequest.headers.environ and request.httprequest.headers.environ[
        'HTTP_X_FORWARDED_FOR']:
        forwarded_for = request.httprequest.headers.environ['HTTP_X_FORWARDED_FOR'].split(', ')
        if forwarded_for and forwarded_for[0]:
            ip = forwarded_for[0]
    return ip


def save_session(sid, type_session='standard', unsuccessful=False):
    session_obj = request.env['ir.sessions']
    cr = request.registry.cursor()

    ip = _get_request_ip()
    # autocommit: our single update request will be performed atomically.
    # (In this way, there is no opportunity to have two transactions
    # interleaving their cr.execute()..cr.commit() calls and have one
    # of them rolled back due to a concurrent access.)
    cr.autocommit(True)
    user = request.env.user
    logged_in = True
    uid = user.id
    if unsuccessful:
        uid = SUPERUSER_ID
        logged_in = False
        sessions = False
    else:
        sessions = session_obj.search([('session_id', '=', sid), ('type_session', '=', type_session), ('ip', '=', ip),
                                       ('user_id', '=', uid), ('logged_in', '=', True)])
    if not sessions:
        values = {
            'user_id': uid,
            'logged_in': logged_in,
            'session_id': sid,
            'last_use': fields.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'type_session': type_session,
            'ip': ip
        }
        session_obj.sudo().create(values)
        cr.commit()
    cr.close()


class Home(odoo.addons.web.controllers.main.Home):
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        if not request.registry.get('ir.sessions'):
            return super(Home, self).web_login(redirect=redirect, **kw)
        odoo.addons.web.controllers.main.ensure_db()

        session_obj = request.env['ir.sessions']
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            has_active_session = False
            if 'login' in request.params and 'password' in request.params:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                user = request.env.user
                sessions = session_obj.search([('user_id', '=', uid), ('type_session', '=', 'standard'), ('logged_in', '=', True)])
                if len(sessions) and user.block_multiple_session:
                    uid = False
                    has_active_session = True

            if uid is not False:
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web'
                save_session(request.httprequest.session.sid)
                return http.redirect_with_hash(redirect)
            save_session(request.httprequest.session.sid, 'standard', True)
            request.uid = old_uid
            if has_active_session:
                values['error'] = _("User has another active session.")
            else:
                values['error'] = _("Wrong login/password")
        return request.render('web.login', values)


class Session(odoo.addons.web.controllers.main.Session):

    @http.route('/web/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        uid = request.session.authenticate(db, login, password)
        if uid is not False:
            save_session(request.httprequest.session.sid, 'movil')
        else:
            save_session(request.httprequest.session.sid, 'movil', True)
        return request.env['ir.http'].session_info()
