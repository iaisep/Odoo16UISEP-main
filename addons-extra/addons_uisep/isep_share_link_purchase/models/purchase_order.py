# -*- coding: utf-8 -*-
import logging
import uuid
from werkzeug.urls import url_encode
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrderLink(models.Model):
    _inherit = 'purchase.order'


    link_static = fields.Char('Enlace', compute = '_compute_share_link_make', store=True)

    def _compute_share_link_make(self):
        for rec in self:
            rec.link_static = False
            if rec.id:
                record = self.browse(rec.id)
                if isinstance(record, self.pool['portal.mixin']):
                    rec.link_static = record.get_base_url() + record._get_share_url(redirect=True)


    @api.model
    def create(self, vals):
        record = super(PurchaseOrderLink, self).create(vals)
        record._compute_share_link_make()
        return record