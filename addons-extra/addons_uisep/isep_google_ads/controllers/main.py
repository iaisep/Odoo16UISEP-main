# -*- coding: utf-8 -*-
import logging
import pprint

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
import json
import werkzeug

_logger = logging.getLogger(__name__)



class PortalController(http.Controller):
    _webhook_url = '/googleads/webhook'
    _auth_key = 'Yh5qGSjT0GYrWQURafEqoNc1z4XzGTsap3SvPDz351L3vP4ZEd'

    @http.route(_webhook_url, type="json" , auth='public')
    def IsepPortalWebhook(self):
        """auth_key = http.request.httprequest.headers.get('X-Auth-Key')  # Obtener la clave de autenticación de la cabecera
        if auth_key != self._auth_key:
            _logger.error("Unauthorized request. Invalid authentication key.")
            return http.Response(status=401)"""

        data = json.loads(request.httprequest.data)
        _logger.info("*******************************************")
        _logger.info("*******************************************")
        _logger.info("Portal data:\n%s", pprint.pformat(data))
        _logger.info("*******************************************")
        _logger.info("*******************************************")
        
        #GRABAR EN LA TABLA 
        try:
            # Check the origin and integrity of the notification
            request.env['isep.google.leads'].sudo()._get_portal_notification_data(data)
           
        except ValidationError:  # Acknowledge the notification to avoid getting spammed
            _logger.exception("unable to handle the notification data; skipping to acknowledge")

        return 'SUCCESS'  # Acknowledge the notification


        