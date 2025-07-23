# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import fields, models


class OpSection(models.Model):
    _name = "op.section"
    _description = "Section"

    name = fields.Char(string='Name', required=True)
    course_ids = fields.Many2many('op.course', string='Course')
    batch_ids = fields.Many2many('op.batch',
                                 domain="[('course_id', '=', course_ids)]",
                                 string='Batch')
    subject_id = fields.Many2one('op.subject',
                                 domain="[('course_id', '=', course_ids)]",
                                 string='Subject')
    student_course_ids = fields.Many2many('op.student.course',
                                          string='Student')
