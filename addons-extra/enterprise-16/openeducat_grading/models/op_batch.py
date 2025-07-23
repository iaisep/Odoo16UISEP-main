# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json

from odoo import _, models


class OpBatch(models.Model):
    _inherit = "op.batch"

    def get_grade_book_grid_data_by_batch(self):
        data = {}
        students_list = []
        batch = self.env['op.batch'].search([('id', '=', self.id)])
        if batch.course_id.grade_scale_id:
            credit = True
        else:
            credit = False
        students = self.env['op.student'].search(
            [('course_detail_ids.batch_id', 'in', [self.id])])
        for student in students:
            students_list.append(student.id)
        progression = self.env['gradebook.gradebook'].search([
            ('student_id', 'in', students_list)])
        # for grade_line in progression.gradebook_line_id:
        #     c_id = grade_line.course_id.id
        #     break
        for p in progression:
            if p.course_id.id == batch.course_id.id:
                data[p.student_id.name] = json.loads(p.gradebook)
        return {'data': json.dumps(data),
                'credit': credit}

    def open_grade_book_grid(self):
        self.ensure_one()
        value = {
            'type': 'ir.actions.client',
            'name': _('GradeBook'),
            'tag': 'grade_book_grid_by_batch',
            'target': 'current',
            'params': {'grade_book': self.id},
        }
        return value
