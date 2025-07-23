# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpGradeScale(models.Model):

    _name = 'op.grade.scale'
    _description = "Grading Scale"

    name = fields.Char('Name', required=True)
    op_grade_type_ids = fields.One2many('op.grade.type', 'op_grade_scale_id',
                                        string='Grade Type')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
