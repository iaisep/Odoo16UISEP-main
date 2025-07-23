# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class ScholarshipStages(models.Model):
    _name = "scholarship.stages"
    _description = "Scholarship Stages"
    name = fields.Char('Name', size=64, required=True)
