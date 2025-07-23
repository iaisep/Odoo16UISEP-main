# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import fields, models


class OpDigitalLibraryReview(models.Model):
    _name = "op.digital.library.material.review"
    _description = "Digital Library Material Review"

    name = fields.Char(string="Name")
    email = fields.Char(string="Email")
    review = fields.Char(string="Review")
    rating = fields.Float(string="Rating")
    material_id = fields.Many2one('op.digital.library.material', string="Material")
    user_id = fields.Many2one('res.users', string="User")
