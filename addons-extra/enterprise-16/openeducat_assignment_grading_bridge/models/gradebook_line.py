###############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GradebookLine(models.Model):
    _inherit = "gradebook.line"

    obtained_marks = fields.Float("Obtained Mark")
    marks = fields.Float('Given Marks', tracking=True)
    penalty = fields.Float('Penalty %')

    @api.onchange('grade_table_line_id', 'marks')
    def _compute_per_by_table_line(self):
        for record in self:
            assignment = self.env['op.assignment'].search([
                ('name', '=', record.grade_assigment_id.name)])

            if record.grade_table_line_id:
                record.percentage = record.grade_table_line_id.percentage
                record.grade_table_id = record.grade_table_line_id.grade_table_id
            elif record.marks:
                if record.marks <= record.grade_assigment_id.point:
                    if assignment:
                        if assignment.assignment_sub_line:
                            for student in assignment.assignment_sub_line:
                                if student.student_id.id == record.gradebook_id.\
                                        student_id.id:
                                    if assignment.late_submission_id:
                                        for late in assignment.late_submission_id:
                                            if late:
                                                if student.\
                                                        submission_date > assignment.\
                                                        submission_date:
                                                    issue_date = assignment.\
                                                        submission_date
                                                    sub_date = student.submission_date
                                                    delta = sub_date - issue_date
                                                    for line in late.late_sub_line:
                                                        if delta.days <= line.\
                                                                no_of_days:
                                                            given_mark = (
                                                                record.
                                                                marks * 100 / record.
                                                                grade_assigment_id.
                                                                point)
                                                            total = (line.
                                                                     penalty / 100
                                                                     ) * given_mark
                                                            record.penalty = line.\
                                                                penalty
                                                            record.percentage = \
                                                                given_mark - total
                                                            # record.percentage = 0.0
                                                            break
                                                        else:
                                                            record.\
                                                                percentage = (
                                                                    record.marks * 100 / record. # noqa
                                                                    grade_assigment_id.point) # noqa
                                                else:
                                                    record.percentage = (
                                                        record.marks * 100 / record.
                                                        grade_assigment_id.point)
                                            else:
                                                record.percentage = (
                                                    record.marks * 100 / record.
                                                    grade_assigment_id.point)
                                    else:
                                        record.percentage = (
                                            record.marks * 100 / record.
                                            grade_assigment_id.point)
                        else:
                            record.percentage = 0.0
                    else:
                        record.percentage = (record.marks * 100 / record.
                                             grade_assigment_id.point)
                else:
                    raise ValidationError(
                        _("Marks should be less than or equal to {}".format(
                            record.grade_assigment_id.point)))
            else:
                record.percentage = 0.0
