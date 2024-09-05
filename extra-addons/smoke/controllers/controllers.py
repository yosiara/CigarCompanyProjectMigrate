# -*- coding: utf-8 -*-
# from odoo import http


# class Smoke(http.Controller):
#     @http.route('/fuma/fuma', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fuma/fuma/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fuma.listing', {
#             'root': '/fuma/fuma',
#             'objects': http.request.env['fuma.fuma'].search([]),
#         })

#     @http.route('/fuma/fuma/objects/<model("fuma.fuma"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fuma.object', {
#             'object': obj
#         })
