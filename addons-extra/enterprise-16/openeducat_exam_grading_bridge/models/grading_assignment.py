# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, models
from odoo.exceptions import ValidationError


class GradingAssigment(models.Model):
    _inherit = 'grading.assignment'

    def create_gradeline(self):
        grade_book = self.env['gradebook.gradebook'].search([
            ('academic_year_id.id', '=', self.year_id.id),
            ('course_id', '=', self.course_id.id)])
        course_detail = self.env['op.student.course'].search([
            ('course_id', '=', self.course_id.id)])
        exam = self.env['op.exam'].search([
            ('subject_id.course_id', '=', self.course_id.id),
            ('subject_id', '=', self.subject_id.id)])
        create_line = self.env['gradebook.line'].search([
            ('grade_assigment_id', '=', self.id)])
        student_list = [student.gradebook_id.student_id.id for student in create_line]
        for name in grade_book:
            if course_detail.subject_ids:
                course_detail = course_detail.search([
                    ('subject_ids', 'in', self.subject_id.id)])
            for data in course_detail:
                if data.student_id.id == name.student_id.id and name.\
                        student_id.id not in student_list:
                    name.gradebook_line_id.create({
                        'gradebook_id': name.id,
                        'academic_year_id': self.year_id.id,
                        'academic_term_id': self.term_id.id,
                        'course_id': self.course_id.id,
                        'subject_id': self.subject_id.id,
                        'assignment_type_id': self.assignment_type.id,
                        'grade_assigment_id': self.id,
                        'grade_table_id': self.grade.id,
                    })
        grade_line = self.env['gradebook.line'].search([
            ('grade_assigment_id', '=', self.id)])
        if self.assignment_type.assign_type == 'exam':
            if exam:
                for lines in grade_line:
                    for mark in exam:
                        for attendes in mark.attendees_line:
                            if lines.gradebook_id.student_id == attendes.student_id:
                                lines.write({
                                    'marks': attendes.marks
                                })
                grade_line._compute_per_by_table_line()
            else:
                raise ValidationError(_("No Exams Results"))
        return {
            'name': 'GradeBook Line',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'gradebook.line',
            'domain': [('grade_assigment_id.id', '=', self.id)]
        }
