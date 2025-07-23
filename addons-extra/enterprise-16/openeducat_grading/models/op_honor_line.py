# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpHonorRollLine(models.Model):
    _name = 'op.honorroll.line'

    _description = "Honor Roll Line"

    student_id = fields.Many2one('op.student', string="Student")
    year_id = fields.Many2one('op.academic.year', string='Academic Year')
    percentage = fields.Float('Percentage')
    course_id = fields.Many2one('op.course', 'Course')
    honor_id = fields.Many2one('op.honorroll', 'Honor')
    subject_id = fields.Many2one('op.subject', string='Subject')
