# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpCourseCategory(models.Model):
    _name = "op.course.category"
    _description = "Course Category"

    name = fields.Char('Name', translate=True, required=True)
    code = fields.Char('Code', required=True)
    desc = fields.Text('Description')
    icon = fields.Char('Icon')
    parent_id = fields.Many2one('op.course.category', 'Parent Category')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    # def action_onboarding_course_category_layout(self):
    #     self.env.user.company_id.onboarding_course_category_layout_state = \
    #         'done'
