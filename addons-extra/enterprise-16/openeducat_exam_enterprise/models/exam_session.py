# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpExamSession(models.Model):
    _inherit = "op.exam.session"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def search_read_for_exam(self):
        if self.env.user.partner_id.is_student:
            main_list = []
            user = self.env.user
            student = self.env['op.student'].sudo().search(
                [('user_id', '=', user.id)])
            values = [i.course_id.id for i in student.course_detail_ids]
            session = self.sudo().search([('course_id', 'in', values),
                                          ('state', 'not in', ['done', 'draft'])])

            for record in session:
                main_dict = {}
                main_dict.update({
                    'id': record.id,
                    'session_name': record.name,
                    'exam_type': record.exam_type.name,
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                    'course_id': record.course_id.id
                })
                sub_list = []
                for exam in record.exam_ids:
                    sub_dict = {}
                    sub_dict.update({
                        'id': exam.id,
                        'session_id': exam.session_id.id,
                        'exam_name': exam.name,
                        'start_time': exam.start_time,
                        'end_time': exam.end_time,
                        'subject_name': exam.subject_id.name,
                        'status': exam.state,
                        'total_marks': exam.total_marks,
                        'passing_marks': exam.min_marks
                    })
                    min_list = []
                    for attendance in exam.attendees_line:
                        min_dict = {}
                        min_dict.update(
                            {
                                'student_name': attendance.student_id.name
                            }
                        )
                        min_list.append(min_dict)
                        sub_dict.update({'student': min_list})
                    sub_list.append(sub_dict)
                    main_dict.update({'exam': sub_list})
                main_list.append(main_dict, )
            return main_list
