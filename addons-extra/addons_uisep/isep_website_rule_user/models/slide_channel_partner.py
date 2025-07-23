# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    auto_added = fields.Boolean(string="Añadido Automáticamente", default=False)
