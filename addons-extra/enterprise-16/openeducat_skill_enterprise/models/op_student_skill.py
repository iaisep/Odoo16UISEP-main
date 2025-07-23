# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudentSkill(models.Model):
    _name = "op.student.skill"
    _description = "Student Skill"
    _rec_name = 'student_skill_name_id'

    student_skill_name_id = fields.Many2one(
        'op.student.skill.name', 'Name', required=True)
    student_skill_type_id = fields.Many2one('op.student.skill.type')
