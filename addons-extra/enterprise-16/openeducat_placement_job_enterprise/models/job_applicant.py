# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpJobApplication(models.Model):
    _inherit = "op.job.applicant"

    activity_id = fields.Many2one("op.activity.announcement",
                                  string="Activity",
                                  readonly=True)
