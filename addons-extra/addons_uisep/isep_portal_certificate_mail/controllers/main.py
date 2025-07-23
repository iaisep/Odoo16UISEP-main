

from odoo import http
from odoo.http import request

class CustomPageController(http.Controller):

    @http.route('/ticket/certificate', type='http', auth='user', website=True)
    def custom_page(self, **kwargs):
        return request.render('isep_portal_certificate_mail.website_ticket_orientacion_universitaria', {})