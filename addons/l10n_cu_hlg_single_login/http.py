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
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from odoo.http import request
from odoo.tools.func import lazy_property
from odoo.http import SessionExpiredException, AuthenticationError, serialize_exception, HttpRequest


_logger = logging.getLogger(__name__)


class JsonRequest(odoo.http.JsonRequest):

    def _handle_exception(self, exception):
        """Called within an except block to allow converting exceptions
           to arbitrary responses. Anything returned (except None) will
           be used as response."""
        try:
            return super(odoo.http.JsonRequest, self)._handle_exception(exception)
        except Exception:
            if not isinstance(exception,
                              (odoo.exceptions.Warning, SessionExpiredException, odoo.exceptions.except_orm)):
                _logger.exception("Exception during JSON request handling.")

            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': serialize_exception(exception)
            }

            if isinstance(exception, AuthenticationError):
                error['code'] = 100
                error['message'] = "Odoo Sesión Inválida"
            if isinstance(exception, SessionExpiredException):
                error['code'] = 100
                error['message'] = "Odoo Sesión Expirada"
                error['data']['debug'] = "Su sesión ha expirado la página se actualizará en unos segundos."
                error['data']['arguments'] = ['Sesión Expirada']
            return self._json_response(error=error)


class OpenERPSession(odoo.http.OpenERPSession):
    def logout(self, keep_db=False, env=None):
        try:
            env = env or request.env
        except:
            pass
        if env and hasattr(env, 'registry') and env.registry.get('ir.sessions'):
            session = env['ir.sessions'].sudo().search([('session_id', '=', self.sid), ('logged_in', '=', True), ])
            if session:
                session._on_session_logout()
        return super(OpenERPSession, self).logout(keep_db=keep_db)


class Root_tkobr(odoo.http.Root):
    @lazy_property
    def session_store(self):
        # Setup http sessions
        path = odoo.tools.config.session_dir
        _logger.debug('HTTP sessions stored in: %s', path)
        return werkzeug.contrib.sessions.FilesystemSessionStore(
            path, session_class=OpenERPSession)

    def get_request(self, httprequest):
        # deduce type of request
        if httprequest.args.get('jsonp'):
            return JsonRequest(httprequest)
        if httprequest.mimetype in ("application/json", "application/json-rpc"):
            return JsonRequest(httprequest)
        else:
            return HttpRequest(httprequest)


root = Root_tkobr()
odoo.http.root.session_store = root.session_store
odoo.http.root.get_request = root.get_request
