# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from _datetime import datetime

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    affiliation_ids = fields.One2many('op.board.affiliation', 'company_id',
                                      'Affiliation Board')

    openeducat_core_onboard_panel = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding core layout step",
        default='not_done')
    onboarding_course_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding course layout step",
        default='not_done')
    onboarding_batch_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding batch layout step",
        default='not_done')
    onboarding_subject_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding subject layout step",
        default='not_done')

    @api.model
    def action_close_core_onboarding(self):
        """ Mark the onboarding panel as closed. """
        self.env.user.company_id.openeducat_core_onboard_panel = 'closed'

    # course layout starts##

    @api.model
    def action_onboarding_course_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_core_enterprise.'
            'action_onboarding_course_layout').read()[0]
        return action

    # batch layout starts#

    @api.model
    def action_onboarding_batch_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_core_enterprise.'
            'action_onboarding_batch_layout').read()[0]
        return action

    # subject layout starts##

    @api.model
    def action_onboarding_subject_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_core_enterprise.'
            'action_onboarding_subject_layout').read()[0]
        return action

    def update_core_onboarding_state(self):
        """ This method is called on the controllers rendering
         method and ensures that the animations
            are displayed only one time. """
        steps = [
            'onboarding_course_layout_state',
            'onboarding_batch_layout_state',
            'onboarding_subject_layout_state'
        ]
        return self._get_and_update_onboarding_state(
            'openeducat_core_onboard_panel', steps)


class ResUsers(models.Model):
    _inherit = "res.users"

    def search_read_for_app(self, offset=0, limit=None, order=None):
        if self.env.user.partner_id.is_student:
            domain = ([('id', '=', self.env.user.id)])
            fields = ['name', 'email', 'image_1920', 'mobile',
                      'country_id', 'city', 'street', 'state_id', 'zip']
            user = self.sudo().search_read(domain=domain, fields=fields,
                                           offset=offset, limit=limit, order=order)
            student = self.env['op.student'].sudo().search(
                [('user_id', '=', self.env.user.id)])
            res = {'user_data': user,
                   'birth_date': student.birth_date,
                   'blood_group': student.blood_group,
                   'gender': student.gender,
                   'student_id': student.id,
                   }
            return res

        elif self.env.user.partner_id.is_parent:
            domain = ([('id', '=', self.env.user.id)])
            fields = ['name', 'email', 'image_1920', 'mobile',
                      'country_id', 'city', 'street', 'state_id', 'zip']
            res = self.sudo().search_read(domain=domain, fields=fields,
                                          offset=offset, limit=limit, order=order)
            return {'user_data': res}

        else:
            domain = ([('id', '=', self.env.user.id)])
            fields = ['name', 'email', 'image_1920', 'mobile', 'country_id',
                      'city', 'street', 'state_id', 'zip']
            user = self.sudo().search_read(domain=domain, fields=fields,
                                           offset=offset, limit=limit, order=order)
            faculty = self.env['op.faculty'].sudo().search(
                [('user_id', '=', self.env.user.id)])
            res = {'user_data': user,
                   'faculty_id': faculty.id,
                   'birth_date': faculty.birth_date,
                   'blood_group': faculty.blood_group,
                   'gender': faculty.gender}
            return res

    # def compute_student_dashboard_data(self, kw=[]):
    #     user_id = kw
    #     total_assignments = 0
    #     total_subs = 0
    #     today_lectures = 0
    #     assigned_books = 0
    #     total_exam = 0
    #     total_event = 0
    #     course_ids = []
    #     if user_id:
    #         ir_model = self.env['ir.model'].sudo()
    #         student = self.env['op.student'].sudo().search(
    #             [('user_id', '=', user_id)], limit=1)
    #         if student:
    #             assignment = ir_model.search([
    #                 ('model', '=', 'op.assignment')])
    #             if assignment:
    #                 total_assignments = self.env['op.assignment'] \
    #                     .sudo().search_count(
    #                     [('allocation_ids', 'in', student.id),
    #                      ('state', '=', 'publish')])
    #                 total_subs = self.env['op.assignment.sub.line'] \
    #                     .sudo().search_count(
    #                     [('student_id', '=', student.id),
    #                      ('state', '=', 'submit'),
    #                      ('assignment_id.state', 'not in', ['finish'])])
    #             batch_ids = [
    #                 record.batch_id.id for record in student.course_detail_ids
    #             ]
    #             course_ids = [
    #                 record.course_id.id for record in student.course_detail_ids
    #             ]
    #             session = ir_model.search([('model', '=', 'op.session')])
    #             if session and batch_ids:
    #                 today_lectures = self.env['op.session'] \
    #                     .sudo().search_count(
    #                     [('state', 'not in', ['draft']),
    #                      ('batch_id', 'in', batch_ids),
    #                      ('start_datetime', '>=',
    #                       datetime.today().strftime('%Y-%m-%d 00:00:00')),
    #                      ('start_datetime', '<=',
    #                       datetime.today().strftime('%Y-%m-%d 23:59:59'))])
    #             library = ir_model.search([
    #                 ('model', '=', 'op.media.movement')])
    #             if library:
    #                 assigned_books = self.env['op.media.movement'] \
    #                     .sudo().search_count(
    #                     [('student_id', '=', student.id),
    #                      ('state', '=', 'issue')])
    #             if student:
    #                 values = []
    #                 for record in student.course_detail_ids:
    #                     values.append(record.course_id.id)
    #
    #             exam_session = ir_model.search([
    #                 ('model', '=', 'op.exam.session')])
    #             if exam_session:
    #                 total_exam = self.env['op.exam.session'].sudo().search_count(
    #                     [('course_id', 'in', values),
    #                      ('state', 'not in', ['done', 'draft'])])
    #
    #             events = ir_model.sudo().search_count(
    #                 [('model', '=', 'event.event')])
    #             if events:
    #                 total_event = self.env['event.event'].sudo().search_count(
    #                     [('state', 'not in', ['draft', 'done'])])
    #
    #             apps = self.env['ir.module.module'].sudo().search(
    #                 ['|', '|', '|', '|', '|',
    #                  ('name', '=', 'openeducat_exam_enterprise'),
    #                  ('name', '=', 'openeducat_assignment_enterprise'),
    #                  ('name', '=', 'openeducat_timetable_enterprise'),
    #                  ('name', '=', 'openeducat_attendance_enterprise'),
    #                  ('name', '=', 'openeducat_library_enterprise'),
    #                  ('name', '=', 'openeducat_event_enterprise')
    #                  ])
    #
    #             assignment = ''
    #             library = ''
    #             exam = ''
    #             attendance = ''
    #             event = ''
    #             timetable = ''
    #
    #             app_name = []
    #             for i in apps:
    #                 app_name.append(i.name)
    #
    #                 if 'openeducat_assignment_enterprise' == i.name:
    #                     assignment = i.state
    #                 if 'openeducat_library_enterprise' == i.name:
    #                     library = i.state
    #                 if 'openeducat_exam_enterprise' == i.name:
    #                     exam = i.state
    #                 if 'openeducat_attendance_enterprise' == i.name:
    #                     attendance = i.state
    #                 if 'openeducat_event_enterprise' == i.name:
    #                     event = i.state
    #                 if 'openeducat_timetable_enterprise' == i.name:
    #                     timetable = i.state
    #
    #     res = {
    #         'student_id': student.id,
    #         'course_ids': course_ids,
    #         'assignment': {
    #             'name': 'Assignments',
    #             'state': assignment,
    #             'count': total_assignments,
    #         },
    #         'submission': {
    #             'name': 'Submissions',
    #             'state': assignment,
    #             'count': total_subs,
    #         },
    #         'library': {
    #             'name': 'Library',
    #             'state': library,
    #             'count': assigned_books,
    #         },
    #         'attendance': {
    #             'name': 'Attendance',
    #             'state': attendance,
    #             'count': '',
    #         },
    #         'exam': {
    #             'name': 'Exam & Result',
    #             'state': exam,
    #             'count': total_exam,
    #         },
    #         'event': {
    #             'name': 'Events',
    #             'state': event,
    #             'count': total_event,
    #         },
    #         'timetable': {
    #             'name': 'Time Table',
    #             'state': timetable,
    #             'count': today_lectures,
    #         },
    #     }
    #     return res

    def compute_faculty_dashboard_data(self, kw=[]): # noqa
        user_id = kw
        total_assignments = 0
        total_subs = 0
        today_lectures = 0
        if user_id:
            faculty = self.env['op.faculty'].sudo().search(
                [('user_id', '=', user_id)], limit=1)
            if faculty:
                ir_model = self.env['ir.model'].sudo()
                assignment = ir_model.search(
                    [('model', '=', 'op.assignment')])
                if assignment:
                    total_assignments = self.env['op.assignment'] \
                        .sudo().search_count(
                        [('faculty_id', '=', faculty.id),
                         ('state', 'in', ['draft', 'publish'])])
                    total_subs = self.env['op.assignment.sub.line'] \
                        .sudo().search_count(
                        [('assignment_id.faculty_id', '=', faculty.id),
                         ('state', '=', 'submit'),
                         ('assignment_id.state', 'not in', ['finish'])])
                session = ir_model.search(
                    [('model', '=', 'op.session')])
                if session:
                    today_lectures = self.env['op.session'] \
                        .sudo().search_count(
                        [('state', 'not in', ['draft']),
                         ('faculty_id', '=', faculty.id),
                         ('start_datetime', '>=',
                          datetime.today().strftime('%Y-%m-%d 00:00:00')),
                         ('start_datetime', '<=',
                          datetime.today().strftime('%Y-%m-%d 23:59:59'))])

        apps = self.env['ir.module.module'].sudo().search(
            ['|', '|', '|',
             ('name', '=', 'openeducat_assignment'),
             ('name', '=', 'openeducat_timetable'),
             ('name', '=', 'openeducat_attendance'),
             ('name', '=', 'openeducat_assignment_grading_enterprise')
             ])

        assignment = ''
        attendance = ''
        timetable = ''
        evaluation = ''

        app_name = []
        for i in apps:
            app_name.append(i.name, )

            if 'openeducat_assignment' == i.name:
                assignment = i.state
            if 'openeducat_attendance' == i.name:
                attendance = i.state
            if 'openeducat_timetable' == i.name:
                timetable = i.state
            if 'openeducat_assignment_grading_enterprise' == i.name:
                evaluation = i.state

        res = {
            'faculty_id': faculty.id,
            'assignment': {
                'name': 'Assignments',
                'state': assignment,
                'count': total_assignments,
            },
            'submission': {
                'name': 'Submissions',
                'state': assignment,
                'count': total_subs,
            },
            'attendance': {
                'name': 'Attendance',
                'state': attendance,
                'count': '',
            },
            'timetable': {
                'name': 'Time Table',
                'state': timetable,
                'count': today_lectures,
            },
            'evalution': {
                'name': 'assignment_grading',
                'state': evaluation
            }
        }
        return res

    def compute_parent_dashboard_data(self, kw=[]): # noqa
        apps = self.env['ir.module.module'].sudo().search(
            ['|', '|', '|',
             ('name', '=', 'openeducat_exam'),
             ('name', '=', 'openeducat_assignment'),
             ('name', '=', 'openeducat_timetable'),
             ('name', '=', 'openeducat_attendance')
             ])

        assignment = ''
        exam = ''
        attendance = ''
        timetable = ''

        app_name = []
        for i in apps:
            app_name.append(i.name, )

            if 'openeducat_assignment' == i.name:
                assignment = i.state
            if 'openeducat_exam' == i.name:
                exam = i.state
            if 'openeducat_attendance' == i.name:
                attendance = i.state
            if 'openeducat_timetable' == i.name:
                timetable = i.state

        res = {
            'assignment': {
                'name': 'Assignments',
                'state': assignment,
                'count': '',
            },
            'submission': {
                'name': 'Submissions',
                'state': assignment,
                'count': '',
            },
            'attendance': {
                'name': 'Attendance',
                'state': attendance,
                'count': '',
            },
            'exam': {
                'name': 'Exam & Result',
                'state': exam,
                'count': '',
            },
            'timetable': {
                'name': 'Time Table',
                'state': timetable,
                'count': '',
            }
        }
        return res
