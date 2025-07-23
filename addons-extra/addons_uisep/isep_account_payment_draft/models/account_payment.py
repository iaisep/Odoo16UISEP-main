# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'



    def send_draft_cancel(self):
        payment_ids = self.browse(self._context.get('active_ids'))

        for payment in payment_ids:
            if payment.state != 'draft':
                payment.action_draft()
                payment.action_cancel()
            

