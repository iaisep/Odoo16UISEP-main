# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudentSkillType(models.Model):
    _name = "op.student.skill.type"
    _description = "Student Skill Types"

    name = fields.Char(string="Name", required=True)
    student_skills_line = fields.One2many(
        'op.student.skill', 'student_skill_type_id', 'Student Skills')
    student_skill_level_line = fields.One2many(
        'op.student.skill.level', 'student_skill_type_id', 'Student Skill Level')
