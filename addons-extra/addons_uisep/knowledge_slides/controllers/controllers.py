# -*- coding: utf-8 -*-
# from odoo import http


# class KnowledgeSlides(http.Controller):
#     @http.route('/knowledge_slides/knowledge_slides', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/knowledge_slides/knowledge_slides/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('knowledge_slides.listing', {
#             'root': '/knowledge_slides/knowledge_slides',
#             'objects': http.request.env['knowledge_slides.knowledge_slides'].search([]),
#         })

#     @http.route('/knowledge_slides/knowledge_slides/objects/<model("knowledge_slides.knowledge_slides"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('knowledge_slides.object', {
#             'object': obj
#         })
