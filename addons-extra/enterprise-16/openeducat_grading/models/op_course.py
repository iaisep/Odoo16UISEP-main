# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json

from odoo import _, fields, models


class OpCourse(models.Model):
    _inherit = "op.course"

    grade_template_ids = fields.Many2many('op.grade.template',
                                          string='Grade Template', required=True)
    grade_scale_id = fields.Many2one('op.grade.scale', string='Final Grade')

    def create_assignment(self):
        return {
            'name': "New Assignment",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'grading.assignment',
            'view_id': self.env.ref('openeducat_grading.'
                                    'view_grading_assignment_form').id,
            'target': 'new'
        }

    def open_grade_book_grid(self):
        self.ensure_one()
        value = {
            'type': 'ir.actions.client',
            'name': _('GradeBook'),
            'tag': 'grade_book_grid_by_course',
            'target': 'current',
            'params': {'grade_book': self.id},
        }
        return value

    def get_grade_book_grid_data_by_course(self):
        data = {}
        students_list = []
        course = self.env['op.course'].search([('id', '=', self.id)])
        if course.grade_scale_id:
            credit = True
        else:
            credit = False
        students = self.env['op.student'].search(
            [('course_detail_ids.course_id', 'in', [self.id])])
        for student in students:
            students_list.append(student.id)
        progression = self.env['gradebook.gradebook'].search([
            ('student_id', 'in', students_list),
            ('course_id', '=', course.id)])
        # for grade_line in progression.gradebook_line_id:
        #     c_id = grade_line.course_id.id
        #     break
        for p in progression:
            print(p.name, p.gradebook)
            if p.gradebook:
                data[p.student_id.name] = json.loads(p.gradebook)
        return {'data': json.dumps(data),
                'credit': credit}
