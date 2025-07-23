# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResCard(models.Model):
    _inherit = 'res.card'

    sale_id = fields.Many2one('sale.order', string="Orden", copy=False)
