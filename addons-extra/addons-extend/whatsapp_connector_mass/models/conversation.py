# -*- coding: utf-8 -*-
from odoo import models


class AcruxChatConversation(models.Model):
    _inherit = 'acrux.chat.conversation'
    _mailing_enabled = True

    def _mailing_get_default_domain(self, mailing):
        return ['|', ('connector_type', '=', 'apichat.io'), ('connector_type', '=', 'gupshup')]
