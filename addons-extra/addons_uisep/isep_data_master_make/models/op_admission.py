# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OpAdmissionMake(models.Model):
    _inherit = 'op.admission'

    order_id = fields.Many2one(
        'sale.order', 
        string='Suscripción',
        )
