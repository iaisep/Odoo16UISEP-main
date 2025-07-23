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


class OpAssignment(models.Model):
    _inherit = "op.assignment"

    grading_assignment_id = fields.Many2one('grading.assignment', 'Grading Assignment',
                                            required=True, ondelete="cascade")
    marks = fields.Float('Marks', tracking=True)
    hide = fields.Boolean(compute='_compute_hide')
    late_submission_id = fields.Many2one('late.submission',
                                         string='Late Submission Criteria')
    mark_update = fields.Boolean('Mark Update')
    attempt = fields.Selection(
        [('first_graded', 'First Graded Attempt'),
         ('last_graded', 'Last Graded Attempt'),
         ('lowest_grade', 'Lowest Grade'),
         ('highest_grade', 'Highest Grade'),
         ('average_of_graded', 'Average of Graded Attempts')],
        'Score Attempt Using', default='first_graded')

    @api.depends('grade')
    def _compute_hide(self):
        if self.grade:
            if self.grade.grade_table_ids:
                self.hide = True
            else:
                self.hide = False
        else:
            self.hide = True

    def update_mark(self):
        date_lst = []
        obtained = []
        marks = []
        for student in self.allocation_ids:
            for obj in self.assignment_sub_line:
                if obj.state == 'accept':
                    self.mark_update = True
                    if student == obj.student_id:
                        date_lst.append(obj.id)
                grading_assignment = self.env['grading.assignment'].search(
                    [('id', '=', self.grading_assignment_id.id)])
                if grading_assignment:
                    grade_book = self.env['gradebook.gradebook'].search([
                        ('student_id.id', '=', obj.student_id.id),
                        ('academic_year_id', '=', self.year_id.id),
                        ('course_id', '=', self.course_id.id)])
                    if grade_book:
                        grade_line = self.env['gradebook.line'].search(
                            [('gradebook_id', '=', grade_book.id),
                             ('grade_assigment_id', '=', grading_assignment.id)])
                        if date_lst:
                            if self.attempt == 'first_graded' or self.\
                                    attempt_type == 'single':
                                if sorted(date_lst)[0] == obj.id:
                                    if grade_line:
                                        grade_line.write({
                                            'marks': obj.marks,
                                            'obtained_marks': obj.obtained_mark
                                        })
                            elif self.attempt == 'last_graded':
                                if sorted(date_lst)[-1] == obj.id:
                                    if grade_line:
                                        grade_line.write({
                                            'marks': obj.marks,
                                            'obtained_marks': obj.obtained_mark
                                        })
                            elif self.attempt == 'lowest_grade':
                                for res in date_lst:
                                    if res == obj.id:
                                        marks.append(obj.marks)
                                        obtained.append(obj.obtained_mark)
                                        if grade_line:
                                            grade_line.write({
                                                'marks': min(marks),
                                                'obtained_marks': min(obtained)
                                            })
                            elif self.attempt == 'highest_grade':
                                for res in date_lst:
                                    if res == obj.id:
                                        marks.append(obj.marks)
                                        obtained.append(obj.obtained_mark)
                                        if grade_line:
                                            grade_line.write({
                                                'marks': max(marks),
                                                'obtained_marks': max(obtained)
                                            })
                            else:
                                for res in date_lst:
                                    if res == obj.id:
                                        marks.append(obj.marks)
                                        obtained.append(obj.obtained_mark)
                                        if grade_line:
                                            grade_line.write({
                                                'marks': sum(marks) / len(marks),
                                                'obtained_marks': sum(
                                                    obtained) / len(obtained)
                                            })
                        grade_line._compute_per_by_table_line()
            marks = []
            obtained = []
            date_lst = []


class OpAssignmentSubLine(models.Model):
    _inherit = "op.assignment.sub.line"

    marks = fields.Float('Given Marks', tracking=True)
    obtained_mark = fields.Float(string="Obtained Marks")
    penalty = fields.Float(string='Penalty %')
    late_submit = fields.Boolean(string='Late Submission',
                                 compute='_compute_late_submission')

    @api.onchange('marks')
    def _compute_late_submission(self):
        for record in self:
            if record.marks <= record.assignment_id.point:
                if record.assignment_id.late_submission_id:
                    if record.assignment_id.submission_date:
                        if record.submission_date > record.assignment_id.\
                                submission_date:
                            record.late_submit = True
                            for late in record.assignment_id.late_submission_id:
                                issue_date = record.assignment_id.submission_date
                                sub_date = record.submission_date
                                delta = sub_date - issue_date
                                for line in late.late_sub_line:
                                    if delta.days <= line.no_of_days:
                                        obtained = (line.penalty / 100) * record.marks
                                        record.penalty = line.penalty
                                        record.obtained_mark = record.marks - obtained
                                        break
                                    # else:
                                    #     record.obtained_mark = record.marks
                        else:
                            record.obtained_mark = record.marks
                            record.late_submit = False
                else:
                    record.obtained_mark = record.marks
                    record.late_submit = False
            else:
                raise ValidationError(
                    _("Marks should be less than or equal to {}".format(
                        record.assignment_id.point)))

    def clear_attempt(self):
        for res in self.assignment_id:
            obj = self.unlink()
            if res.mark_update:
                res.update_mark()
            return obj
