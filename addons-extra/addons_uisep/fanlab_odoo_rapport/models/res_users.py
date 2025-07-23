# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import contextlib

import pytz
import datetime
import ipaddress
import itertools
import logging
import hmac

from collections import defaultdict
from hashlib import sha256
from itertools import chain, repeat
from lxml import etree
from lxml.builder import E
import passlib.context

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
from odoo.osv import expression
from odoo.service.db import check_super
from odoo.tools import partition, pycompat, collections

_logger = logging.getLogger(__name__)

class Users(models.Model):
    _inherit = 'res.users'
    active_isep = fields.Boolean(string='Operante')

    @api.model
    def _get_login_domain(self, login):
        return [('login', '=', login),('active_isep','=',True)]

    @classmethod
    def _login(cls, db, login, password):
        if not password:
            raise AccessDenied()
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                with self._assert_can_auth():
                    user = self.with_context(
    active_test=False).search(self._get_login_domain(login))
                    if not user:
                        raise AccessDenied()
                    user = user.sudo(user.id)
                    user._check_credentials(password)
                    user._update_last_login()
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
            raise

        _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)

        return user.id

