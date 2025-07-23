# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpJobpost(models.Model):
    _inherit = "op.job.post"

    skill_ids = fields.Many2many("op.student.skill.name", string="Skills")


class OpSkillLine(models.Model):
    _name = "op.skill.line"
    _description = "Skill Lines Creation Creation"

    skill_type_id = fields.Many2one(
        'op.student.skill.name', string='Skill', required=True)
    student_id = fields.Many2one('op.student', string='student')
    level_id = fields.Many2one('op.student.skill.level.name', string='Level')
    progress = fields.Integer(related='level_id.progress')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)


class OpStudent(models.Model):
    _inherit = "op.student"

    skill_line = fields.One2many(
        'op.skill.line', 'student_id', 'Skills Details')
