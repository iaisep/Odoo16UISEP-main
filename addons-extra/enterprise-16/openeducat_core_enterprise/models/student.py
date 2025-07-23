# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpStudent(models.Model):
    _inherit = "op.student"

    student_badge_ids = fields.One2many(
        'op.badge.student', 'student_id', 'Badges')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    student_count = fields.Integer(compute='_compute_count_student',
                                   readonly=True, store=True)

    def search_read_for_app(
            self, fields=None, offset=0, limit=None, order=None):

        if self.env.user.partner_id.is_student:
            domain = [('user_id', '=', self.env.user.id)]
            res = self.sudo().search_read(domain=domain,
                                          fields=fields,
                                          offset=offset,
                                          limit=limit, order=order)
            return res

        elif self.env.user.partner_id.is_parent:
            parent = self.env['op.parent'].sudo().search(
                [('user_id', '=', self.env.user.id)])
            domain = [('parent_ids', '=', parent.id)]
            res = self.sudo().search(domain)
            student_details = []
            for student in res:
                student_dict = {
                    'id': student.id,
                    'name': student.name,
                    'last_name': student.last_name,
                    'image': student.image_1920,
                    'course': '',
                    'user_id': student.user_id.id,
                    'course_id': ''
                }
                student_details.append(student_dict)

                course_list = []
                course_id = []
                course = ''
                for rec in student.course_detail_ids:
                    course_list.append(rec.course_id.name)
                    course = course + rec.course_id.name + ', <br/>'
                    course_id.append(rec.course_id.id)
                course_detail = course[:-7]
                student_dict['course'] = course_detail
                student_dict['course_id'] = course_id
            return student_details

    def get_student(self):
        action = self.env.ref('openeducat_core.'
                              'act_open_op_student_course_view').read()[0]
        action['domain'] = [('student_id', 'in', [self.id])]
        return action

    @api.depends('course_detail_ids')
    def _compute_count_student(self):
        for record in self:
            record.student_count = len(record.course_detail_ids)

    def get_course_batch_data(self, course_ids):
        courses = ''
        batches = ''
        for course in course_ids:
            courses += course.course_id.name + ', '
            batches += course.batch_id.name + ', '
        return {'courses': courses[:-2], 'batches': batches[:-2]}
