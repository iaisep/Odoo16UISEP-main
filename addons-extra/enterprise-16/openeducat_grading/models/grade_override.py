# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json

from odoo import api, fields, models


class OpGradeOverride(models.Model):

    _name = 'op.grade.override'
    _description = "Grading Override"
    _rec_name = "grade_grade_id"

    course_id = fields.Many2one('op.course', string="Course", required=True)
    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year',
                                       required=True)
    grade_override_line_id = fields.One2many('op.grade.override.line',
                                             'grade_override_id',
                                             string='Grade override Line')
    grade_grade_id = fields.Many2one('gradebook.gradebook', 'Student', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.onchange('grade_grade_id', 'course_id', 'academic_year_id')
    def calculate_term_subject(self):
        if self.academic_year_id:
            if not self.grade_override_line_id:
                subject = self.env['op.subject'].sudo().search([])
                students = self.env['gradebook.gradebook'].search([])
                for student in students:
                    if student.student_id == self.grade_grade_id.student_id:
                        terms = json.loads(student.gradebook)
                        for key, value in terms.items():
                            for rec in self.academic_year_id.academic_term_ids:
                                if key == rec.name:
                                    self.write({
                                        'grade_override_line_id': [(0, 0, {
                                            'term': key,
                                            'calculated': value['Total'],
                                            'grade': value['Grade'] if 'Grade' in value else None, # noqa
                                            'final': value['Grade'] if 'Grade' in value else None # noqa
                                        })]
                                    })
                            if type(value) is str or type(value) is float:
                                pass
                            else:
                                for temp, values in value.items():
                                    for rec in self.academic_year_id.academic_term_ids:
                                        if temp == rec.name:
                                            self.write({
                                                'grade_override_line_id': [(0, 0, {
                                                    'term': temp,
                                                    'calculated': value[temp]['Total'],
                                                    'grade':value[temp]['Grade'] if 'Grade' in value[temp] else None, # noqa
                                                    'final': value[temp]['Grade'] if 'Grade' in value[temp] else None # noqa
                                                })]
                                            })
                                    if type(values) is str or type(values) is float:
                                        pass
                                    else:
                                        for sub in values or []:
                                            for rec in subject:
                                                if sub == rec.name:
                                                    self.write({
                                                        'grade_override_line_id': [
                                                            (0, 0, {
                                                                'term': temp,
                                                                'subject': sub,
                                                                'calculated':
                                                                    values[sub]['Mark'],
                                                                'grade': values[sub]['Grade'] if 'Grade' in values[sub] else None, # noqa
                                                                'final': values[sub]['Grade'] if 'Grade' in values[sub] else None # noqa
                                                            })]
                                                    })
                            if type(value) is str or type(value) is float:
                                pass
                            else:
                                for sub in value:
                                    for rec in subject:
                                        if sub == rec.name:
                                            self.write({
                                                'grade_override_line_id': [(0, 0, {
                                                    'term': key,
                                                    'subject': sub,
                                                    'calculated': value[sub]['Mark'],
                                                    'grade': value[sub]['Grade'] if 'Grade' in value[sub] else None, # noqa
                                                    'final': value[sub]['Grade'] if 'Grade' in value[sub] else None # noqa
                                                })]
                                            })

    @api.onchange('grade_override_line_id')
    def calculate_override_grade(self):
        for i in self.grade_override_line_id: # noqa
            subject = self.env['op.subject'].sudo().search([])
            students = self.env['gradebook.gradebook'].search([])
            quarter_average = []
            sem_average = []
            semester_average = []
            year_average = []
            for student in students:
                if student.student_id == self.grade_grade_id.student_id:
                    terms = json.loads(student.gradebook)
                    for key, value in terms.items():
                        if type(value) is str or type(value) is float:
                            pass
                        else:
                            for key1, value1 in value.items():
                                if type(value1) is float:
                                    pass
                                else:
                                    for sub in value1 or []:
                                        for a in self.grade_override_line_id:
                                            for rec in subject:
                                                if key1 == a.term:
                                                    if sub == rec.name:
                                                        if sub == a.subject:
                                                            if a.override:
                                                                for scale in self.\
                                                                        course_id.\
                                                                        grade_scale_id.op_grade_type_ids: # noqa
                                                                    if (a.override >= scale.min_percentage) and (a.override < scale.max_percentage):  # noqa
                                                                        grade = scale.\
                                                                            name
                                                                        a.final =\
                                                                            grade
                                                                value1[sub]['Mark'] = a.override # noqa
                                                                value1[sub]['Grade'] = a.final # noqa
                                                                quarter_average.append(float(value1[sub]['Mark'])) # noqa
                                                            else:
                                                                quarter_average.\
                                                                    append(float(
                                                                    value1[sub]['Mark'])) # noqa

                                                            if a.comment:
                                                                value1[sub]['Comment'] = a.comment  # noqa
                                            if key == a.term:
                                                if key1 == a.subject:
                                                    if a.override:
                                                        for scale in self.\
                                                                course_id.\
                                                                grade_scale_id.\
                                                                op_grade_type_ids:
                                                            if (a.override >= scale.min_percentage) and (a.override < scale.max_percentage):  # noqa
                                                                grade = scale.name
                                                                a.final = grade
                                                        value1['Mark'] = a.override
                                                        value1['Grade'] = a.final
                                                        semester_average.append(
                                                            float(value1['Mark']))
                                                    else:
                                                        semester_average.append(
                                                            float(value1['Mark']))

                                                    if a.comment:
                                                        value1.update({
                                                            'Comment': a.comment})
                                    if quarter_average:
                                        for a in self.grade_override_line_id:
                                            if key1 == a.term:
                                                if not a.subject:
                                                    if a.override:
                                                        for scale in self.\
                                                                course_id.\
                                                                grade_scale_id.\
                                                                op_grade_type_ids:
                                                            if (a.override >= scale.min_percentage) and (a.override < scale.max_percentage):  # noqa
                                                                grade = scale.name
                                                                a.final = grade
                                                        value[key1]['Total'] = \
                                                            a.override
                                                        value[key1]['Grade'] = a.\
                                                            final
                                                        sem_average.append(
                                                            float(value[key1]
                                                                  ['Total']))
                                                    else:
                                                        average = (sum(
                                                            quarter_average) / len(
                                                            quarter_average))
                                                        sem_average.append(average)
                                                        value[key1]['Total'] = \
                                                            "{:0.2f}".format(
                                                                average)
                                                    if a.comment:
                                                        value[key1]['Comment'] = a.\
                                                            comment
                                    quarter_average = []
                            if sem_average:
                                for a in self.grade_override_line_id:
                                    if key == a.term:
                                        if not a.subject:
                                            if a.override:
                                                for scale in self.course_id.\
                                                        grade_scale_id.\
                                                        op_grade_type_ids:
                                                    if (a.override >= scale.min_percentage) and (a.override < scale.max_percentage):  # noqa
                                                        grade = scale.name
                                                        a.final = grade
                                                value['Total'] = a.override
                                                value['Grade'] = a.final
                                                sem = float(value['Total'])
                                                year_average.append(sem)
                                            else:
                                                sem = (sum(sem_average) / len(
                                                    sem_average))
                                                year_average.append(sem)
                                            if a.comment:
                                                value['Comment'] = a.comment
                                            value['Total'] = "{:0.2f}".format(sem)
                                            # a.final = value['Total']

                            elif semester_average:
                                for a in self.grade_override_line_id:
                                    if key == a.term:
                                        if not a.subject:
                                            if a.override:
                                                for scale in self.course_id.\
                                                        grade_scale_id.\
                                                        op_grade_type_ids:
                                                    if (a.override >= scale.min_percentage) and (a.override < scale.max_percentage):  # noqa
                                                        grade = scale.name
                                                        a.final = grade
                                                value['Total'] = a.override
                                                value['Grade'] = a.final
                                                sem = float(value['Total'])
                                                year_average.append(sem)
                                            else:
                                                sem = (sum(semester_average) / len(
                                                    semester_average))
                                                year_average.append(sem)
                                            if a.comment:
                                                value['Comment'] = a.comment
                                            value['Total'] = "{:0.2f}".format(sem)
                                            # a.final = value['Total']
                                semester_average = []
                        sem_average = []
                        semester_average = []
                    if year_average:
                        terms['Year Total'] = "{:0.2f}".format(
                            sum(year_average) / len(year_average))
                    students = self.env['op.student.progression'].search([])
                    if student.student_id == self.grade_grade_id.student_id:
                        student.gradebook = json.dumps(terms, indent=4)
                    for student in students:
                        if student.student_id == self.grade_grade_id.student_id:
                            student.grade_book = json.dumps(terms, indent=4)
