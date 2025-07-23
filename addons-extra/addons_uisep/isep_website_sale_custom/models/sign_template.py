# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SignTemplate(models.Model):
    _inherit = 'sign.template'

    share_link_website = fields.Char(string="Share Link", compute='_compute_share_link_website')
    
    def _compute_share_link_website(self):
        sign_request = self.env['sign.request'].sudo().search([('template_id', '=', self.id)], limit=1)
        if sign_request:
            self.share_link_website = "%s/sign/document/mail/%s/%s" % (self.get_base_url(), sign_request.id, sign_request.request_item_ids[0].sudo().access_token)
        else:
            self.share_link_website = "Sin link de firma"

    
    def create_link_sign(self):
        self.ensure_one()
        shared_sign_request = self.sign_request_ids.filtered(lambda sr: sr.state == 'shared' and sr.create_uid == self.env.user)
        if not shared_sign_request:
            if len(self.sign_item_ids.mapped('responsible_id')) > 1:
                raise ValidationError(_("You cannot share this document by link, because it has fields to be filled by different roles. Use Send button instead."))
            shared_sign_request = self.env['sign.request'].with_context(no_sign_mail=True).create({
                'template_id': self.id,
                'request_item_ids': [Command.create({'role_id': self.sign_item_ids.responsible_id.id or self.env.ref('sign.sign_item_role_default').id})],
                'reference': "%s-%s" % (self.name, _("Shared")),
                'state': 'shared',
            })
