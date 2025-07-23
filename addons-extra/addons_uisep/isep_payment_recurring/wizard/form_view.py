# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class isep_payment_recurring_wizard(models.TransientModel):
    _name = 'isep.payment.recurring.wizard'

    invoice_id = fields.Many2one('account.move')
    invoice_payment_url = fields.Char('URL')
    

    def default_get(self, fields):
        base_url = self.get_base_url()
        c = super(isep_payment_recurring_wizard, self).default_get(fields)
        invoice_id = self._context['get_invoice_id']
        c['invoice_id'] = invoice_id
        c['invoice_payment_url'] = ('/').join((base_url,"payments/v1/checkout/sessions",str(invoice_id)))
        return c
