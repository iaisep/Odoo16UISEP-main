# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartnerSepyc(models.Model):
    _inherit = 'res.partner'

    record = fields.Text('Historial')
