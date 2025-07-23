# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.tests import TransactionCase, common

from ..controllers import main, onboard


class TestAttendanceCommon(common.TransactionCase):
    def setUp(self):
        super(TestAttendanceCommon, self).setUp()
        self.op_attendance_line = self.env['op.attendance.line']
        self.op_attendance_register = self.env['op.attendance.register']
        self.op_attendance_sheet = self.env['op.attendance.sheet']
        self.op_batch = self.env['op.batch']
        self.op_company = self.env['res.company']
        self.op_progression = self.env['op.student.progression']


class AttendanceControllerTests(TransactionCase):
    def setUp(self):
        super(AttendanceControllerTests, self).setUp()
        self.AttendanceController = onboard.OnboardingController()


# class TestAttendanceController(AttendanceControllerTests):
#
#     def setUp(self):
#         super(TestAttendanceController, self).setUp()
#
#     def test_case_attendance_onboarding(self):
#         self.AttendanceController = onboard.OnboardingController()
#         with MockRequest(self.env):
#             self.cookies = self.\
#                 AttendanceController.openeducat_attendance_onboarding_panel()


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):
    def setUp(self):
        super(TestUi, self).setUp()
        self.attendance_portal = main.AttendancePortal()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = "student"
        parent = self.env['res.users'].search(
            [('login', '=', 'parent@openeducat.com')])
        parent.login = "parent"

    # def test_01_admin_checkout(self):
    #     self.start_tour("/", 'test_attendance', login="student")
    #     self.start_tour("/", 'test_attendance', login="parent")
