# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models


class OpCourseLevel(models.Model):
    _name = "op.course.level"
    _description = "Course Level"

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Course Level'),
            'template': '/openeducat_lms/static/xls/course_level.xls'
        }]
