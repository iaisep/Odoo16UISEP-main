# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from logging import info

from .test_student_attendance_common import TestStudentAttendanceCommon


class TestAttendanceLine(TestStudentAttendanceCommon):

    def setUp(self):
        super(TestAttendanceLine, self).setUp()

    def test_case_student_attendance_line(self):
        line = self.op_student_attendance_line.search([])
        if not line:
            raise AssertionError(
                'Error in data, please check for student attendance details')
        info('  Details Of Student Attendance:.....')
        for record in line:
            record._default_student()
            record.name_get()


class TestStudent(TestStudentAttendanceCommon):

    def setUp(self):
        super(TestStudent, self).setUp()

    def test_case_student_attendance(self):
        student = self.op_student.search([])
        if not student:
            raise AssertionError(
                'Error in data, please check for student attendance details')
        info('  Details Of Student Attendance:.....')
        for record in student:
            record._default_random_pin()
            record.generate_random_barcode()
            record.attendance_scan('student.barcode')
            record._compute_last_attendance_id()
            record._verify_pin()
            record.attendance_action_change()
            record.get_attendance_sheets(student[1].id)
