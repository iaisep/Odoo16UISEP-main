# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json

from odoo import _, fields, models


class StudentGradeProgression(models.Model):
    _inherit = ["op.student.progression"]

    grade_book = fields.Char(string='GradeBook')

    def open_grade_book_grid(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'name': _('GradeBook'),
            'tag': 'grade_book_grid',
            'target': 'current',
            'params': {'grade_book': self.id}
        }

    def get_student_data_grade_book(self):
        data = []
        student = self.env['op.student.progression'].search([])
        for rec in student:
            data.append({
                'name': rec.student_id.name,
                'id': rec.id
            })
        return data

    def get_student_data_grade_book_by_batch(self):
        data = []
        course = self.env['op.batch'].search([])
        for rec in course:
            data.append({
                'name': rec.name,
                'id': rec.id
            })
        return data

    def get_student_data_grade_book_by_student(self):
        data = []
        course = self.env['op.subject'].search([])
        for rec in course:
            data.append({
                'name': rec.name,
                'id': rec.id
            })
        return data

    def get_student_data_grade_book_by_course(self):
        data = []
        course = self.env['op.course'].search([])
        for rec in course:
            data.append({
                'name': rec.name,
                'id': rec.id
            })
        return data

    def get_grade_book_grid_data(self):
        return self.grade_book

    def Refresh_attendance(self):
        attendance = self.env['gradebook.gradebook'].sudo().search([
            ('student_id', '=', self.student_id.id)])
        attendance.calculate_attendance()

    def get_year_total_in_report(self, c_id):
        student = self.env['op.student.progression'].search([('id', '=', int(c_id))])
        gradebook = json.loads(student.grade_book)
        for key, value in gradebook.items(): # noqa
            if type(value) is not dict:
                return value
