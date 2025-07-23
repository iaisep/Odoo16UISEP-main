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

from odoo.addons.website.tools import MockRequest

from ..controllers import onboard


class TestLmsCommon(common.TransactionCase):
    def setUp(self):
        super(TestLmsCommon, self).setUp()
        self.op_material = self.env['op.material']
        self.lms_onboard = self.env['res.company']
        self.lms_op_course = self.env['op.course']
        self.op_course_section = self.env['op.course.section']
        self.op_course_material = self.env['op.course.material']
        self.material_reminder = self.env['material.reminder']
        self.op_quiz_result = self.env['op.quiz.result']
        self.course_invitation = self.env['course.invitation']


class LmsContollerTests(TransactionCase):

    def setUp(self):
        super().setUp()
        self.lmscontroller = onboard.LmsOnboardingController()


class TestLmsController(LmsContollerTests):

    def setUp(self):
        super(TestLmsController, self).setUp()

    def test_quiz_onboard(self):
        with MockRequest(self.env):
            self.onboard = self.lmscontroller.openeducat_lms_onboarding_panel()


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

    def test_01_course(self):
        self.start_tour("/", 'lms_test', login="student")
        self.start_tour("/", 'lms_test', login="parent")

    def test_02_my_course_details(self):
        self.start_tour("/", "course_details_test", login="student")
