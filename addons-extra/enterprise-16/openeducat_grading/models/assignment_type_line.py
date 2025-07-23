# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class SubTermWeightLine(models.Model):

    _name = 'assignment.type.weight.line'
    _description = "Assignment Type Weight Line"
    _rec_name = "assignment_type_id"

    assignment_type_id = fields.Many2one('grading.assignment.type', 'Assignment Type')
    weightage = fields.Float('Weightage')
    grade_templates_id = fields.Many2one('op.grade.template.line', 'Grade Template')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
