# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from random import choice
from string import digits

from odoo import _, api, exceptions, fields, models


class OpStudent(models.Model):
    _inherit = "op.student"
    _description = "Student"

    def _default_random_pin(self):
        return ("0000")

    def generate_random_barcode(self):
        for employee in self:
            employee.barcode = "".join(choice(digits) for i in range(8))

    barcode = fields.Char(string="Badge ID",
                          help="ID used for student identification",
                          default=generate_random_barcode, copy=False)
    pin = fields.Char(string="PIN", default=_default_random_pin,
                      help="PIN used to Sign In in Kiosk Mode", copy=False)
    attendance_ids = fields.One2many('op.attendance.line', 'student_id',
                                     help='list of attendances for students')
    last_attendance_id = fields.Many2one('op.attendance.line',
                                         compute='_compute_last_attendance_id',
                                         store=True)

    _sql_constraints = [('barcode_uniq', 'unique (barcode)',
                         "The Badge ID must be unique, \
                         this one is already assigned to another student.")]

    @api.model
    def attendance_scan(self, barcode):
        sheets = {}

        student_ids = self.env['op.student'].search(
            [('barcode', '=', barcode)], limit=1)
        if student_ids and student_ids.course_detail_ids:
            sheets.update({'student_id': student_ids.id,
                           'student_name': student_ids.name})
        else:
            return {'warning':
                    _('No student corresponding to barcode %(barcode)s')
                    % {'barcode': barcode}}
        return sheets

    @api.model
    def get_attendance_sheets(self, student_id):
        sheets = {}
        sheet_list = []
        max_dict = {}

        student_ids = self.env['op.student'].search([('id', '=', student_id)])
        if student_ids and student_ids.course_detail_ids:
            for courses in student_ids.course_detail_ids:
                register_id = self.env['op.attendance.register'].search(
                    [('course_id', '=', courses.course_id.id),
                     ('batch_id', '=', courses.batch_id.id)])
                if register_id:
                    for register in register_id:
                        sheet_id = self.env['op.attendance.sheet'].search(
                            [('register_id', '=', register.id),
                             ('state', '=', 'start')])
                        if sheet_id:
                            for sheet in sheet_id:
                                student_list = []
                                attendance_lines = sheet.attendance_line
                                if attendance_lines:
                                    for attendance in attendance_lines:
                                        student_list.append(
                                            attendance.student_id.id)
                                    if student_ids.id not in set(student_list):
                                        sheets.update({sheet.id: sheet.name})
                                        sheet_list.append(sheet.id)
                                else:
                                    sheets.update({sheet.id: sheet.name})
                                    sheet_list.append(sheet.id)
        if sheet_list:
            is_selected = max(sheet_list)
            max_dict = {'is_selected': is_selected}

        return sheets, max_dict

    @api.depends('attendance_ids')
    def _compute_last_attendance_id(self):
        for student in self:
            student.last_attendance_id = self.env['op.attendance.line'].search(
                [('student_id', '=', student.id)],
                limit=1)

    @api.constrains('pin')
    def _verify_pin(self):
        for student in self:
            if student.pin and not student.pin.isdigit():
                raise exceptions.ValidationError(
                    _("The PIN must be a sequence of digits."))

    def attendance_manual(self, next_action, entered_pin=None, att_id=0):
        self.ensure_one()
        if entered_pin != self.pin:
            return {'warning': _('Wrong PIN')}
        return self.attendance_action(next_action, att_id)

    def attendance_action(self, next_action, att_id=0):

        self.ensure_one()
        action_message = self.env.ref(
            'openeducat_student_attendance_enterprise.'
            'student_attendance_action_greeting_message'
        ).sudo().read()[0]
        action_message[
            'previous_attendance_change_date'
            ] = self.last_attendance_id and (
            self.last_attendance_id.check_in) or False
        action_message['student_name'] = self.name
        action_message['barcode'] = self.barcode
        action_message['next_action'] = next_action

        if self.user_id:
            modified_attendance = self.with_user(self.user_id.id).sudo().\
                attendance_action_change(att_id)
        else:
            modified_attendance = self.sudo().attendance_action_change(att_id)
        action_message['attendance'] = modified_attendance.sudo().read()[0]
        return {'action': action_message}

    def attendance_action_change(self, att_id=0):

        if len(self) > 1:
            raise exceptions.UserError(
                _('Cannot perform sign in on multiple students.'))
        action_date = fields.Datetime.now()
        vals = {
            'student_id': self.id,
            'check_in': action_date,
            'attendance_id': int(att_id) if att_id else False,
        }
        return self.env['op.attendance.line'].sudo().create(vals)
