# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpGradeTemplate(models.Model):

    _name = 'op.grade.template'
    _description = "Grade Template"

    name = fields.Char(string="Name", required=True)
    template_line_ids = fields.One2many('op.grade.template.line', 'grade_template_id',
                                        string='Template Line', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
