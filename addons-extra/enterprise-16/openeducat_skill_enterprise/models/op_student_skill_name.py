# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudentSkillName(models.Model):
    _name = "op.student.skill.name"
    _description = "Student Skill Name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    skill_category_type_id = fields.Many2one(
        'op.skill.category', string='Skill Type', required=True)
    active = fields.Boolean(default=True)
    self_assessed = fields.Boolean()
