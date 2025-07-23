# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright(C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import api, fields, models


class OpAssignmentSubLines(models.Model):
    _inherit = "op.assignment.sub.line"

    grades_id = fields.Many2one('op.assign.grade.config', string="Grades")
    evaluation_boolean = fields.Boolean("Evaluation Boolean")

    @api.onchange("assignment_id")
    def hide_grade(self):
        if self.assignment_id.evaluation_type == 'grade':
            self.evaluation_boolean = True
        else:
            self.evaluation_boolean = False


class OpAssignment(models.Model):
    _inherit = "op.assignment"

    # grade = fields.Char('Grade', compute='_compute_grades')
    evaluation_type = fields.Selection(
        [('mark', 'Marks'), ('grade', 'Grade')],
        'Evolution type', default="mark",
        required=True, tracking=True)
