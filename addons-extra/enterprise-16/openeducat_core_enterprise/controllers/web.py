# from odoo.http import requests
from odoo import http
from odoo.http import request

from odoo.addons.website.controllers.main import Website


class Web(Website):

    @http.route()
    def website_configurator(self, step=1, **kwargs):
        super(Web, self).website_configurator()
        website_id = request.env['website'].get_current_website()
        if website_id.configurator_done is False:
            return request.render('openeducat_core_enterprise.'
                                  'web_configurator', {'lang': request.env.user.lang})
        else:
            return request.redirect('/')
