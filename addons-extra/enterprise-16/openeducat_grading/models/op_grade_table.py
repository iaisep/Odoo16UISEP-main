# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpGradeTable(models.Model):

    _name = 'op.grade.table'
    _description = "Grade Table"

    name = fields.Char(string="Name", required=True)
    grade_table_ids = fields.One2many('op.grade.table.line', 'grade_table_id',
                                      string='Grade Lines', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
