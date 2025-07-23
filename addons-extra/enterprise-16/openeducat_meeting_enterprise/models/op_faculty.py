# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, models


class OpFaculty(models.Model):
    _inherit = "op.faculty"

    @api.model_create_multi
    def create(self, vals):
        res = super(OpFaculty, self).create(vals)
        faculty = self.env['res.partner.category'].search(
            [('name', '=', 'Faculty')], limit=1)
        partner_id = res.partner_id
        partner_id.write({'category_id': [(6, 0, faculty.ids)]}),
        return res
