# -*- coding: utf-8 -*-
# from odoo import http


# class BisaAgent(http.Controller):
#     @http.route('/bisa_agent/bisa_agent/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bisa_agent/bisa_agent/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bisa_agent.listing', {
#             'root': '/bisa_agent/bisa_agent',
#             'objects': http.request.env['bisa_agent.bisa_agent'].search([]),
#         })

#     @http.route('/bisa_agent/bisa_agent/objects/<model("bisa_agent.bisa_agent"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bisa_agent.object', {
#             'object': obj
#         })
