# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OpBatch(models.Model):
    _inherit = 'op.batch'

    date_start_class = fields.Date('Fecha de inicio de clases')
