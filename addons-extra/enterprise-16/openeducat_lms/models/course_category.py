# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, models


class OpCourseCategory(models.Model):
    _inherit = "op.course.category"

    def action_onboarding_course_category_layout(self):
        self.env.user.company_id.onboarding_course_category_layout_state = \
            'done'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Course Category'),
            'template': '/openeducat_lms/static/xls/course_category.xls'
        }]
