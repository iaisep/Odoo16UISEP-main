# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class LateSubmission(models.Model):
    _name = 'late.submission'
    _description = "Late Submission"

    name = fields.Char('Name')
    late_sub_line = fields.One2many('late.submission.line', 'late_submission_id',
                                    'Late Submission')
