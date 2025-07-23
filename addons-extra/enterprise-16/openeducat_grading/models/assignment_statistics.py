# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import statistics

from odoo import models


class AssignmentStatistics(models.Model):
    _name = "assignment.statistics"
    _description = "Assignment Statistics"

    def _qweb_prepare_qcontext(self, view_id, domain):
        values = super()._qweb_prepare_qcontext(view_id, domain)
        counts = self.static_data(values)
        if counts:
            values.update(counts)
        return values

    def static_data(self, values):
        grades = []
        need_grade = []
        distribute = {}
        state_data = {}
        assign_line = self.env['gradebook.line'].search([
            ('grade_assigment_id', '=', values['context']['active_id'])])
        count = self.env['gradebook.line'].search_count([
            ('grade_assigment_id', '=', values['context']['active_id'])])
        assigned_id = values['context']['active_id']
        if assign_line:
            for values in assign_line:
                if values.marks or values.grade_table_line_id:
                    grades.append(values.marks if values.
                                  marks else values.grade_table_line_id.percentage)
                else:
                    need_grade.append(values.id)
            assignment_name = assign_line.grade_assigment_id.name
            assignment_point = assign_line.grade_assigment_id.point
            minimum_value = sorted(grades)[0] if grades else 0
            maximum_value = sorted(grades)[-1] if grades else 0
            sta_range = maximum_value - minimum_value
            average = sum(grades) / len(grades) if grades else 0
            median = statistics.median(grades) if grades else 0
            if len(grades) == 2:
                std_deviation = "{:0.2f}".format(statistics.stdev(grades))
                variances = statistics.variance(grades)
            else:
                std_deviation = 0
                variances = 0

            for table in assign_line.course_id.grade_scale_id.op_grade_type_ids:
                minimum = table.min_percentage
                maximum = table.max_percentage
                distribution = self.env['gradebook.line'].search_count([
                    ('grade_assigment_id', '=', assigned_id),
                    ('percentage', '>=', minimum),
                    ('percentage', '<=', maximum)])
                distribute.update({"{} - {}".format(minimum, maximum): distribution})
            state_data.update({'assignment_name': assignment_name,
                               'assignment_point': assignment_point,
                               'count': count,
                               'minimum_value': minimum_value,
                               'maximum_value': maximum_value,
                               'sta_range': sta_range,
                               'average': average,
                               'median': median,
                               'std_deviation': std_deviation,
                               'variances': variances,
                               'graded': len(grades),
                               'need_grade': len(need_grade),
                               'grade_count': distribute
                               })
            return state_data

    class StudentStatistics(models.Model):
        _name = "student.statistics"
        _description = "Student Statistics"

        def _qweb_prepare_qcontext(self, view_id, domain):
            values = super()._qweb_prepare_qcontext(view_id, domain)
            counts = self.grading_statistics_data(values)
            if counts:
                values.update(counts)
            return values

        def grading_statistics_data(self, values):
            grades = []
            grades_given = []
            student_data = {}
            grade_book_id = values['context']['active_id']
            grade_book = self.env['gradebook.line'].search([
                ('gradebook_id', '=', grade_book_id),
                ('assignment_type_id.assign_type', '!=', 'attendance')])
            grades_published = self.env['gradebook.line'].search_count([
                ('gradebook_id', '=', grade_book_id),
                ('assignment_type_id.assign_type', '!=', 'attendance'),
                ('grade_assigment_id.state', '=', 'grades_published')])
            grades_archieve = self.env['gradebook.line'].search_count([
                ('gradebook_id', '=', grade_book_id),
                ('assignment_type_id.assign_type', '!=', 'attendance'),
                ('grade_assigment_id.state', '=', 'grades_published'),
                ('grade_assigment_id.active', '!=', True)])
            student_name = grade_book.gradebook_id.student_id.name
            gradebook_name = grade_book.gradebook_id.name

            for grades_count in grade_book:
                if grades_count.marks or grades_count.grade_table_line_id:
                    grades_given.append(grades_count.id)
                else:
                    grades.append(grades_count.id)

            grade_att = []
            grades_given_att = []
            grade_attendance = self.env['gradebook.line'].search([
                ('gradebook_id', '=', grade_book_id),
                ('assignment_type_id.assign_type', '=', 'attendance')])
            att_grades_publish = self.env['gradebook.line'].search_count([
                ('gradebook_id', '=', grade_book_id),
                ('assignment_type_id.assign_type', '=', 'attendance'),
                ('grade_assigment_id.state', '=', 'grades_published'),
                ('grade_assigment_id.active', '=', True)])
            att_grades_archive = self.env['gradebook.line'].search_count([
                ('gradebook_id', '=', grade_book_id),
                ('assignment_type_id.assign_type', '=', 'attendance'),
                ('grade_assigment_id.state', '=', 'grades_published'),
                ('grade_assigment_id.active', '!=', True)])
            for atten in grade_attendance:
                if atten.marks:
                    grades_given_att.append(atten.id)
                else:
                    grade_att.append(atten.id)

            student_data.update({'student_name': student_name,
                                 'gradebook_name': gradebook_name,
                                 'graded': len(grades_given),
                                 'grades_published': grades_published,
                                 'need_grading': len(grades),
                                 'grades_archieve': grades_archieve,
                                 'grades_given_att': len(grades_given_att),
                                 'att_grades_publish': att_grades_publish,
                                 'grade_att': len(grade_att),
                                 'att_grades_archive': att_grades_archive
                                 })
            return student_data
