# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import Controller, request
from odoo.tools import ustr

class FileDispatcher(Controller):
    @http.route('/custom_download_file/', type='http', auth='user')
    def dispatch_file(self, data, token):
        _data = json.loads(data)
        _obj_class = request.env[_data['model']]
        _obj = _obj_class.search([('id', '=', _data['record_id'])])[0]

        return request.make_response(
            _obj.get_file(),
            cookies={'fileToken': token},
            headers=[
                ('Content-Type', _obj.get_content_type()),
                ('Content-Disposition', u'attachment; filename={}'.format(ustr(_obj.get_filename())))
            ],
        )
