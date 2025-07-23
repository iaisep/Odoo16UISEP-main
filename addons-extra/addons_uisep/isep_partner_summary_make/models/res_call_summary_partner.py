# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResCallSummaryPartner(models.Model):
    _name = 'res.call.summary.partner'
    _description = 'ResCallSummaryPartner'

    partner_id = fields.Many2one('res.partner', string='Contacto')
    summary = fields.Text('Resumen')
