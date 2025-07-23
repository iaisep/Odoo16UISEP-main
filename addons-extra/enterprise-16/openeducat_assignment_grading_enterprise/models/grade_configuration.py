# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright(C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import fields, models


class OpAssignGradeConfig(models.Model):
    _name = "op.assign.grade.config"
    _rec_name = "grade"
    _description = "Grade Configuration"

    grade = fields.Char('Grade', required=True)
