# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleTemporalRecurrence(models.Model):
    _inherit = 'sale.temporal.recurrence'

    use_public_auto = fields.Boolean('Usar Para Venta desde Website', default=False)
