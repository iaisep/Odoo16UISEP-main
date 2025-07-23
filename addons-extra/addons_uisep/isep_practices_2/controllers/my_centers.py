# -*- coding: utf-8 -*-


from odoo import http
from odoo.http import request
from odoo.tools import json
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers import portal

class PracticeCenterPortal2(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        # _logger.info('_prepare_home_portal_values',counters)

        if not 'practice_centers_count' in counters:
            counters.append('practice_centers_count')

        values = super()._prepare_home_portal_values(counters)
        if 'practice_centers_count' in counters:
            values['practice_centers_count'] = request.env['practice.center'].sudo().search_count([
                # ('create_uid', '=', request.env.user.id)
                ('email', '=', request.env.user.email)
            ])
            if values['practice_centers_count']==0:
                values['practice_centers_count']="Nuevo"



        return values
class PracticeCenterPortal(http.Controller):

   

    @http.route(['/my/centers'], type='http', auth='user', website=True)
    def practice_centers(self, **kw):
        # Obtener los centros de práctica registrados para el usuario
        centers = request.env['practice.center'].search([
            # ('create_uid', '=', request.env.user.id)
            ('email', '=', request.env.user.email)
            ])

        # Pasar los datos a la vista
        return request.render('isep_practices_2.practice_centers_template', {
            'centers': centers,
        })

    @http.route(['/my/practice_center/<int:center_id>'], type='http', auth='user', website=True)
    def portal_practice_center(self, center_id, **kwargs):
        center = request.env['practice.center'].browse(center_id)
        if not center.exists():
            return request.not_found()
        return request.render('isep_practices_2.portal_practice_center', {'doc': center})