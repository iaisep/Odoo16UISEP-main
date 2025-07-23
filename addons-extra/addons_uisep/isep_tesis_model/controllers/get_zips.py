# -*- coding: utf-8 -*-


from odoo import http
from odoo.http import request
from odoo.tools import json
from odoo.addons.portal.controllers.portal import CustomerPortal



class PracticeCenterPortal(http.Controller):
 
    @http.route('/get_zips/<int:state_id>', type='http', auth='public', methods=['GET'])
    def get_zips(self, state_id):
        if not state_id:
            return request.make_response(
                json.dumps({'error': 'Invalid state ID'}),
                headers=[('Content-Type', 'application/json')]
            )

        zips = request.env['res.city.zip'].search([('state_id', '=', state_id)])
        data = [{'id': zip.id, 'name': f"{zip.city_id.name} - {zip.name}"} for zip in zips]
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

