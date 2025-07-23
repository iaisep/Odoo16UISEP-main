# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class LateSubmissionLine(models.Model):
    _name = 'late.submission.line'
    _description = "Late Submission Line"

    no_of_days = fields.Float('Days')
    penalty = fields.Float('Penalty')
    late_submission_id = fields.Many2one('late.submission', string='Late Submission')
