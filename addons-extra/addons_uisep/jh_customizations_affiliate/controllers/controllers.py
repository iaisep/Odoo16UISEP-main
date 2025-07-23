# -*- coding: utf-8 -*-
# from odoo import http


# class JhCustomizationsAffiliate(http.Controller):
#     @http.route('/jh_customizations_affiliate/jh_customizations_affiliate', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jh_customizations_affiliate/jh_customizations_affiliate/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jh_customizations_affiliate.listing', {
#             'root': '/jh_customizations_affiliate/jh_customizations_affiliate',
#             'objects': http.request.env['jh_customizations_affiliate.jh_customizations_affiliate'].search([]),
#         })

#     @http.route('/jh_customizations_affiliate/jh_customizations_affiliate/objects/<model("jh_customizations_affiliate.jh_customizations_affiliate"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jh_customizations_affiliate.object', {
#             'object': obj
#         })
