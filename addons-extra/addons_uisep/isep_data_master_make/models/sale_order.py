# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderMake(models.Model):
    _inherit = 'sale.order'

    def name_get(self):
        result = []
        for record in self:
            if self.env.context.get('show_partner_name_make'):
                name = f"[{record.name}] - {record.partner_id.name}"
            else:
                name = record.name
            result.append((record.id, name))
        return result
