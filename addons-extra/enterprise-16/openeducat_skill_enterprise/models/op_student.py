# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudent(models.Model):
    _inherit = "op.student"

    student_skill_line = fields.One2many(
        'op.student.skill.line', 'student_id', 'Student Skills')
