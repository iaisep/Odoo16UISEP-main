# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudentSkillLine(models.Model):
    _name = "op.student.skill.line"
    _description = "Student Skill Line"
    _rec_name = 'student_skill_type_id'

    student_id = fields.Many2one('op.student')
    student_skill_type_id = fields.Many2one(
        'op.student.skill.type', required=True, string='Skill Type')
    student_skills_id = fields.Many2one(
        'op.student.skill', required=True,
        domain="[('student_skill_type_id', '=', student_skill_type_id)]",
        string='Skills')
    student_skill_level_id = fields.Many2one(
        'op.student.skill.level', required=True,
        domain="[('student_skill_type_id', '=', student_skill_type_id)]",
        string='Skill Level')
    progress = fields.Integer(related='student_skill_level_id.progress')
