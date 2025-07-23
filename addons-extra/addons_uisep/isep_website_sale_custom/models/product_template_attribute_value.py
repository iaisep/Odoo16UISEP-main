# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    plazo = fields.Integer('Plazo')
