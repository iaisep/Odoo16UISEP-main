# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpFaculty(models.Model):
    _inherit = "op.faculty"

    bio_data = fields.Html('Bio Data')
    designation = fields.Char('Designation')
