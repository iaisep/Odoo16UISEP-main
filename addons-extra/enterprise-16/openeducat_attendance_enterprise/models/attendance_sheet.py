# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from datetime import datetime

from odoo import api, fields, models


class OpAttendanceSheet(models.Model):
    _inherit = 'op.attendance.sheet'

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    subject_id = fields.Many2one('op.subject', string='Subject')
    section_id = fields.Many2one('op.section', string='Section')

    @api.depends('attendance_line')
    def _compute_get_attendance(self):
        for obj in self:
            for line in obj.attendance_line:
                if line.present is True:
                    obj.total_present += 1
                elif line.absent is True:
                    obj.total_absent += 1
                elif line.excused is True:
                    obj.excused_count += 1
                elif line.late is True:
                    obj.late_count += 1
            obj.total_present = obj.total_present or 0
            obj.total_absent = obj.total_absent or 0
            obj.excused_count = obj.excused_count or 0
            obj.late_count = obj.late_count or 0
        return True

    total_present = fields.Integer(
        string='Total Present',
        compute='_compute_get_attendance',
        readonly=True)

    total_absent = fields.Integer(
        string='Total Absent',
        compute='_compute_get_attendance',
        readonly=True)

    excused_count = fields.Integer(
        string='Total Absent Excused',
        compute='_compute_get_attendance',
        readonly=True)

    late_count = fields.Integer(
        string='Total Late',
        compute='_compute_get_attendance',
        readonly=True)

    @api.onchange('subject_id')
    def onchange_subject_id(self):
        self.section_id = False
        if self.subject_id:
            section_ids = self.env['op.section']. \
                search([('subject_id', '=', self.subject_id.id)])
            return {'domain': {'section_id': [('id', 'in', section_ids.ids)]}}

    def action_onboarding_attendance_sheet_layout(self):
        self.env.user.company_id.onboarding_attendance_sheet_layout_state = \
            'done'

    def attendance_sheet_daily(self):
        register_ids = self.env['op.attendance.register'].search(
            [('auto_create', '=', True)])
        for register in register_ids:
            if register.auto_create_type == 'daily':
                self.create({
                    'register_id': register.id,
                    'course_id': register.course_id.id or False,
                    'batch_id': register.batch_id.id or False,
                    'subject_id': register.subject_id.id or False,
                    'section_id': register.section_id.id or False,
                })

    def attendance_sheet_weekly(self):

        register_ids = self.env['op.attendance.register'].search(
            [('auto_create', '=', True)])
        for register in register_ids:
            if register.auto_create_type == 'weekly':
                self.create({
                    'register_id': register.id,
                    'course_id': register.course_id.id or False,
                    'batch_id': register.batch_id.id or False,
                    'subject_id': register.subject_id.id or False,
                    'section_id': register.section_id.id or False,
                })

    def attendance_sheet_monthly(self):
        register_ids = self.env['op.attendance.register'].search(
            [('auto_create', '=', True)])
        for register in register_ids:
            if register.auto_create_type == 'monthly':
                self.create({
                    'register_id': register.id,
                    'course_id': register.course_id.id or False,
                    'batch_id': register.batch_id.id or False,
                    'subject_id': register.subject_id.id or False,
                    'section_id': register.section_id.id or False,
                })

    def attendance_sheet_daily_if_session(self):
        register_ids = self.env['op.attendance.register'].search(
            ['|', ('auto_create_if_session', '=', True),
             ('auto_create', '=', True)])
        session_ids = self.env['op.session'].search([])
        for register in register_ids:
            if register.auto_create_if_session:
                for session in session_ids:
                    start_datetime = session.start_datetime.date()
                    end_datetime = session.end_datetime.date()
                    if register.course_id == session.course_id:
                        if register.batch_id == session.batch_id:
                            if register.subject_id == session.subject_id:
                                current_date = datetime.today().date()
                                if str(start_datetime) <= str(current_date) \
                                        <= str(end_datetime):
                                    self.create({
                                        'register_id': register.id,
                                        'course_id': register.course_id.id,
                                        'batch_id': register.batch_id.id,
                                        'session_id': session.id
                                    })

    def new_create_attendance_lines(self, kw=[]): # noqa
        sheet_id = kw
        if sheet_id:
            attend_lines = self.env['op.attendance.line'].sudo()
            sheet = self.env['op.attendance.sheet'].sudo().browse(
                sheet_id)
            all_student_search = self.env['op.student'].sudo().search(
                [('course_detail_ids.course_id', '=',
                  sheet.register_id.course_id.id),
                 ('course_detail_ids.batch_id', '=',
                  sheet.register_id.batch_id.id)])
            attendance_lines = attend_lines.search(
                [('attendance_id', '=', sheet.id)])
            students = [record.id for record in all_student_search]
            attendance = [record.student_id.id for record in attendance_lines]
            remaining_students = set(students).difference(attendance)
            for student in remaining_students:
                attend_lines.create({
                    'attendance_id': sheet.id,
                    'student_id': student,
                    'attendance_date': fields.Date.today(),
                    'present': True
                })
        return True

    def attendance_start(self):
        res = super(OpAttendanceSheet, self).attendance_start()
        if self.register_id:
            attendance_lines = [qq.student_id.id for qq in
                                self.env['op.attendance.line'].search(
                                    [('attendance_id', '=', self.id)])]
            if self.register_id.section_id:
                for student in self.register_id.section_id.student_course_ids:
                    if student.student_id.id not in attendance_lines:
                        self.attendance_line.create({
                            'student_id': student.student_id.id,
                            'present': True,
                            'attendance_id': self.id
                        })
            elif self.register_id.course_id and self.register_id.batch_id:
                all_student_search = self.env['op.student.course'].search([
                    ('course_id', '=', self.register_id.course_id.id),
                    ('batch_id', '=', self.register_id.batch_id.id)])
                for student in all_student_search:
                    if student.student_id.id not in attendance_lines:
                        self.attendance_line.create({
                            'student_id': student.student_id.id,
                            'present': True,
                            'attendance_id': self.id
                        })
            elif self.register_id.subject_id:
                all_student_search = self.env['op.student.course'].search([
                    ('subject_ids', 'in', self.register_id.subject_id.id)])
                for student in all_student_search:
                    if student.student_id.id not in attendance_lines:
                        self.attendance_line.create({
                            'student_id': student.student_id.id,
                            'present': True,
                            'attendance_id': self.id
                        })
        return res

    def total_present_count(self):
        action = None
        for rec in self.attendance_line: # noqa
            action = self.env.ref('openeducat_attendance.'
                                  'act_open_op_attendance_line_view').read()[0]
            action['domain'] = [('attendance_id', 'in', self.ids),
                                ('present', '=', True)]
        return action

    def total_absent_count(self):
        action = None
        for rec in self.attendance_line: # noqa
            action = self.env.ref('openeducat_attendance.'
                                  'act_open_op_attendance_line_view').read()[0]
            action['domain'] = [('attendance_id', 'in', self.ids),
                                ('absent', '=', True)]
        return action

    def total_excused_count(self):
        action = None
        for rec in self.attendance_line: # noqa
            action = self.env.ref('openeducat_attendance.'
                                  'act_open_op_attendance_line_view').read()[0]
            action['domain'] = [('attendance_id', 'in', self.ids),
                                ('excused', '=', True)]
        return action

    def total_late_count(self):
        action = None
        for rec in self.attendance_line: # noqa
            action = self.env.ref('openeducat_attendance.'
                                  'act_open_op_attendance_line_view').read()[0]
            action['domain'] = [('attendance_id', 'in', self.ids),
                                ('late', '=', True)]
        return action
