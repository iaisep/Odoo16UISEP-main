# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudentSkillLevelName(models.Model):
    _name = "op.student.skill.level.name"
    _description = "Student Skill Level Name"

    name = fields.Char(required=True)
    progress = fields.Integer(required=True)
