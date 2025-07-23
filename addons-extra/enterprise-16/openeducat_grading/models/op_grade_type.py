# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpGradeType(models.Model):

    _name = 'op.grade.type'
    _description = "Grading Type"

    name = fields.Char('Name', required=True)
    earn_credits = fields.Boolean('Earn Credits')
    gpa_value = fields.Float('GPA')
    min_percentage = fields.Float('Minimum Percentage')
    max_percentage = fields.Float('Maximum Percentage')
    include_gpa = fields.Boolean('Include GPA')
    op_grade_scale_id = fields.Many2one('op.grade.scale', 'Grade scale')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    form_factor = fields.Boolean('Form Factor')
    factor = fields.Float('Factor', default=10)
