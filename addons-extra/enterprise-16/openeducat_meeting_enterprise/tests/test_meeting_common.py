# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.tests import TransactionCase, common

from ..controller import onboard


class TestMeetingCommon(common.TransactionCase):
    def setUp(self):
        super(TestMeetingCommon, self).setUp()
        self.op_meeting = self.env['op.meeting']


class MeetingContollerTests(TransactionCase):

    def setUp(self):
        super().setUp()
        self.MeetingContollerTests = onboard.OnboardingController()


class TestMeetingController(MeetingContollerTests):

    def setUp(self):
        super(TestMeetingController, self).setUp()

    # def test_case_meeting_onboard(self):
    #     self.MeetingContollerTests = onboard.OnboardingController()
    #     with MockRequest(self.env):
    #         self.cookies = self.MeetingContollerTests. \
    #             openeducat_meeting_onboarding_panel()


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = "student"
        parent = self.env['res.users'].search(
            [('login', '=', 'parent@openeducat.com')])
        parent.login = "parent"

    def test_01_meeting_information_data(self):
        self.start_tour("/", "test_meeting_information_data", login="student")
        self.start_tour("/", "test_meeting_information_data", login="parent")
