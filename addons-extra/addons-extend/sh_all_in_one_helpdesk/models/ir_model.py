# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_create_multi
    def create(self, vals):
        res = super(IrAttachment, self).create(vals)
        if res.res_model and res.res_id and res.res_model == 'sh.helpdesk.ticket':
            res.public = True
        return res


class IrModel(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def xmlid_to_res_model_res_id(self, xmlid, raise_if_not_found=False):
        return self._xmlid_to_res_model_res_id(xmlid, raise_if_not_found)[1]
