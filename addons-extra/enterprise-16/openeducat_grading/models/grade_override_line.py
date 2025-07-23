# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpGradeOverrideLine(models.Model):
    _name = 'op.grade.override.line'
    _description = "Grading Override Line"
    _rec_name = "term"

    grade_grade_id = fields.Many2one('gradebook.gradebook', 'Student')

    year = fields.Many2one('op.academic.year', string='Year')
    term = fields.Many2one('op.academic.term', string='Terms')
    subject = fields.Many2one('op.subject', string='Subject')
    calculated = fields.Char(string='Calculated')
    grade = fields.Char('Grade')
    override = fields.Float(string="Override")
    final = fields.Char(string='Final')
    comment = fields.Char(string="Comment")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
