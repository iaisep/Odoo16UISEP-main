# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class SubTermWeightLine(models.Model):

    _name = 'subterm.weight.line'
    _description = "Sub Term Weight Line"
    _rec_name = "academic_sub_term_id"

    academic_sub_term_id = fields.Many2one('op.academic.term', 'Sub Terms',
                                           required=True)
    weightage = fields.Float('Weightage')
    grade_template_id = fields.Many2one('op.grade.template.line', 'Grade Template')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
