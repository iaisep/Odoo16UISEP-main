# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class GrievanceRootCause(models.Model):
    _name = "grievance.root.cause"
    _description = "Grievance Root Cause"

    name = fields.Char("Name")
