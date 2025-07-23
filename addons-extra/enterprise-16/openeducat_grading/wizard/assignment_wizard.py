# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AssignmentWizard(models.TransientModel):
    _name = "assignment.wizard"
    _description = "Assignment Wizard"

    def _get_assign_domain(self):
        grade = self.env['gradebook.gradebook'].browse(
            self.env.context.get('active_id'))
        return [('year_id', 'in', grade.academic_year_id.ids),
                ('course_id', '=', grade.course_id.id)]

    assignment_ids = fields.Many2many(
        'grading.assignment', string='Assignment', domain=_get_assign_domain)

    def action_confirm_assignment(self):
        self.ensure_one()
        book = self.env['gradebook.gradebook'].browse(self.env.context.get('active_id'))
        line_data = []
        for line in self.assignment_ids:
            grade_line = self.env['gradebook.line'].search([
                ('grade_assigment_id', '=', line.id)])
            student_list = [
                student.gradebook_id.student_id.id for student in grade_line]

            if book.student_id.id not in student_list:
                line_data.append([0, False, {
                    'gradebook_id': book.id,
                    'academic_year_id': line.year_id.id,
                    'academic_term_id': line.term_id.id,
                    'course_id': line.course_id.id,
                    'subject_id': line.subject_id.id,
                    'assignment_type_id': line.assignment_type.id,
                    'grade_assigment_id': line.id,
                    'grade_table_id': line.grade.id,
                }])
            else:
                raise ValidationError(_("{} Assignment already added".format(line.
                                                                             name)))
        book.gradebook_line_id = line_data
