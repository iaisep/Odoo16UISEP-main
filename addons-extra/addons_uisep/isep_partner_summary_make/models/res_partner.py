# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    summary_ids=fields.One2many(
        'res.call.summary',
        'partner_id',string="Resúmen de llamadas lead")

    summary_partner_ids=fields.One2many(
        'res.call.summary.partner',
        'partner_id',string="Resúmen de llamadas contacto")
