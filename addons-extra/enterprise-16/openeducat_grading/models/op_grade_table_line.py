# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpGradeTableLine(models.Model):

    _name = 'op.grade.table.line'
    _description = "Grade Table Line"

    name = fields.Char(string="Name", required=True)
    percentage = fields.Float(string="Percentage", required=True)
    grade_table_id = fields.Many2one('op.grade.table', 'Grade Table')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
