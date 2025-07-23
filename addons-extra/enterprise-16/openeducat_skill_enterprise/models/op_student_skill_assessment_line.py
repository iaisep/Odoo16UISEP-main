# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudentSkillAssessmentLine(models.Model):
    _name = "op.student.skill.assessment.line"
    _description = "Student Skill Assessment"
    _rec_name = 'student_skill_id'

    student_skill_type_id = fields.Many2one(
        'op.student.skill.type', 'Skill Assessment Type')
    student_skill_id = fields.Many2one(
        'op.student.skill',
        domain="[('student_skill_type_id', '=', student_skill_type_id)]",
        required=True)
    student_skill_level_id = fields.Many2one(
        'op.student.skill.level',
        domain="[('student_skill_type_id', '=', student_skill_type_id)]")
    student_skill_assessment_id = fields.Many2one('op.student.skill.assessment')
    progress = fields.Integer(related='student_skill_level_id.progress')
