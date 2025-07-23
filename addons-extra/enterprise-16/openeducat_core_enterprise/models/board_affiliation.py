# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpBoardAffiliation(models.Model):
    _name = "op.board.affiliation"
    _description = "Board Affiliation"

    name = fields.Char('Board Name')
    code = fields.Char('Code')
    note = fields.Text('Description')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)
