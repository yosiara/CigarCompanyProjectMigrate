# -*- coding: utf-8 -*-

# Alejandro Cora González
# alek.cora.glez@gmail.com

import json

from odoo import http
from odoo.http import Controller, request
from odoo.tools import ustr


class FileDispatcher(Controller):
    @http.route('/download_custom_file/', type='http', auth='user')
    def dispatch_file(self, data, token):
        _data = json.loads(data)
        _obj_class = request.env[_data['model']]
        _obj = _obj_class.search([('id', '=', _data['record_id'])])[0]

        response = request.make_response(_obj.get_file(), headers=[
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document;charset=utf-8;'),
            ('Content-Disposition', u'attachment; filename={};'.format(ustr(_obj.get_filename())))
        ], cookies={
            'fileToken': token
        })

        return response
FileDispatcher()
