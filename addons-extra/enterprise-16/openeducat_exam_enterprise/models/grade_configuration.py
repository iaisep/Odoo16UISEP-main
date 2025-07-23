# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpGradeConfiguration(models.Model):
    _inherit = "op.grade.configuration"
    _description = "Grade Configuration"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def action_onboarding_exam_grade_layout(self):
        self.env.user.company_id.onboarding_exam_grade_layout_state = 'done'
