# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class SurveySurvey(models.Model):
    _name = "survey.survey"
    _inherit = "survey.survey"

    course_id = fields.Many2one('op.course', 'Course')
