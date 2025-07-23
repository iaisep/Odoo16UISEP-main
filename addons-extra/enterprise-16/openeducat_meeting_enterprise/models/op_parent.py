# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, models


class OpParent(models.Model):
    _inherit = "op.parent"

    @api.model_create_multi
    def create(self, vals):
        res = super(OpParent, self).create(vals)
        parent = self.env['res.partner.category'].search(
            [('name', '=', 'Parent')])
        partner_id = res.name
        partner_id.write({'category_id': [(6, 0, parent.ids)]}),
        return res
