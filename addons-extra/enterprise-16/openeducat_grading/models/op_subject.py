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


class OpSubject(models.Model):
    _inherit = "op.subject"

    grade_template_ids = fields.Many2many('op.grade.template',
                                          string='Grade Template', required=True)
    parent_sub_id = fields.Many2one('op.subject', 'Parent Subject')
    default_template = fields.Boolean('Use Default Course Template', default=True)

    def get_grade_book_grid_data_by_subject(self):
        data = {}
        students_list = []
        subject = self.env['op.subject'].search([('id', '=', self.id)])
        if subject.course_id.grade_scale_id:
            credit = True
        else:
            credit = False
        students = self.env['op.student'].search(
            [('course_detail_ids.course_id', 'in', [subject.course_id.id])])
        for student in students:
            students_list.append(student.id)
        progression = self.env['gradebook.gradebook'].search([
            ('student_id', 'in', students_list)])
        # for grade_line in progression.gradebook_line_id:
        #     c_id = grade_line.course_id.id
        #     break
        for p in progression:
            if p.course_id.id == subject.course_id.id:
                data[p.student_id.name] = json.loads(p.gradebook)
        return {'data': json.dumps(data),
                'credit': credit,
                'subject': subject.name,
                'subject_code': subject.code}

    def open_grade_book_grid(self):
        self.ensure_one()
        value = {
            'type': 'ir.actions.client',
            'name': _('GradeBook'),
            'tag': 'grade_book_grid_by_subject',
            'target': 'current',
            'params': {'grade_book': self.id},
            'domain': []
        }
        return value
