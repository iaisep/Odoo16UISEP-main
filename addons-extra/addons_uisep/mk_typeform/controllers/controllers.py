# -*- coding: utf-8 -*-

import json
import logging
from ..tools import tools
from ..exceptions.custom_exceptions import InvalidJson
from odoo import http, _
from odoo.http import request

logger = logging.getLogger(__name__)


class TypeFormController(http.Controller):

    @http.route(['/typeform/webhook'], type="json", auth="public")
    def send_typeform(self, **kwargs):
       # logger.info("Request ====================================: %s " % (request.dispatcher.jsonrequest))
        try:
            response = request.dispatcher.jsonrequest
            tools.convert_response_to_form(response)
            return self._status_response('200', 'OK', _("Form has been successfully registered"))
        except InvalidJson as e:
            return self._status_response('404', 'NOT_FOUND', e)

    def _status_response(self, code, status, description=""):
        return {
            'code': code,
            'status': status,
            'description': description
        }
