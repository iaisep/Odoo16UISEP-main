# -*- coding: utf-8 -*-


from odoo import http
from odoo.http import request
from odoo.tools import json
from odoo.addons.portal.controllers.portal import CustomerPortal


class PracticeCenterPortal(http.Controller):
    @http.route('/get_states/<int:country_id>', type='http', auth='public', methods=['GET', 'POST'])
    def get_states(self, country_id=None):
        if request.httprequest.method == 'POST':
            data = request.jsonrequest
            country_id = data.get('country_id', country_id)
        if not country_id:
            return request.make_response(json.dumps({'error': 'Invalid country ID'}),
                                         headers=[('Content-Type', 'application/json')])
        states = request.env['res.country.state'].search([('country_id', '=', country_id)])
        data = [{'id': state.id, 'name': state.name} for state in states]
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])

