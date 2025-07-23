# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DataFlywire(models.Model):
    _name = 'data.flywire'
    _description = _('Data flywire')

    name = fields.Char(_('Name'))
    api_key = fields.Char(_('Api Key'), required=True)
    url_create_session = fields.Char(_('URL Create Session'), required=True)
    url_create_payment = fields.Char(string='URL Create Payment', required=True)
    shared_secret = fields.Char(string='Shared Secret', required=True)
    url_website_webhook = fields.Char(string='https://webhook.site/')
    active_url_website_webhook = fields.Boolean(_('Active webhook'))
    active = fields.Boolean(_('Active'), default=True) 

