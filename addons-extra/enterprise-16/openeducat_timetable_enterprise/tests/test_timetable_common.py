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

from ..controller import onboard


class TestTimetableCommon(common.TransactionCase):
    def setUp(self):
        super(TestTimetableCommon, self).setUp()
        self.op_batch = self.env['op.batch']
        self.op_session = self.env['op.session']
        self.op_timing = self.env['op.timing']
        self.op_company = self.env['res.company']


class TimetableControllerTests(TransactionCase):
    def setUp(self):
        super(TimetableControllerTests, self).setUp()
        self.TimetableController = onboard.OnboardingController()


class TestTimetableController(TimetableControllerTests):

    def setUp(self):
        super(TestTimetableController, self).setUp()

    # def test_case_timetable_onboarding(self):
    #     self.TimetableController = onboard.OnboardingController()
    #     with MockRequest(self.env):
    #         self.cookies = \
    #             self.TimetableController.openeducat_timing_onboarding_panel()


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = "student"

    # Script used in url template
    # def test_01_test_student_timetable(self):
    #     self.start_tour("/", 'test_timetable', login="student")
