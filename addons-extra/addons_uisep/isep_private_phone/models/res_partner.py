# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartnerPhone(models.Model):
    _inherit = 'res.partner'

    is_manager = fields.Boolean(compute='_compute_is_manager')


    def _compute_is_manager(self):
        for record in self:
            record.is_manager = self.env.user.has_group('isep_private_phone.isep_group_manager_phone')
    
