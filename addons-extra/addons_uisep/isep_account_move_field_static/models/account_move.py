# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMoveFieldStatic(models.Model):
    _inherit = 'account.move'

    phone = fields.Char('Teléfono')
    email = fields.Char('Email')

    @api.model
    def create(self, vals):
        res = super(AccountMoveFieldStatic, self).create(vals)
        phone_partner = res.partner_id.phone
        email_partner = res.partner_id.email
        res.phone = phone_partner
        res.email = email_partner
        return res