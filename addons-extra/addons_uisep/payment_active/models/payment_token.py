# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PaymentTokenInherit(models.Model):
    _inherit = 'payment.token'



    def write(self, values):
        if 'active' in values and not values['active']:
            self.filtered('active').sudo()._handle_archiving()

        return super(models.Model, self).write(values)
