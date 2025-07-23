# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudentSkillLevel(models.Model):
    _name = "op.student.skill.level"
    _description = "Student Skill Level"
    _rec_name = 'student_skill_level_name_id'

    student_skill_level_name_id = fields.Many2one('op.student.skill.level.name', 'Name')
    progress = fields.Integer(related='student_skill_level_name_id.progress')
    student_skill_type_id = fields.Many2one('op.student.skill.type')
