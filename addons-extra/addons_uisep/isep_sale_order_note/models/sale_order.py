# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderNote(models.Model):
    _inherit = 'sale.order'

    internal_note_record = fields.Text()
    state_paid = fields.Selection([
        ('active', 'Activo'),
        ('moroso', 'Moroso'),
        ('low', 'Baja'),
        ('paid', 'Liquidado'),
    ], string="Estado de Pago")
