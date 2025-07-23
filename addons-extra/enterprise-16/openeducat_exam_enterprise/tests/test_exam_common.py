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

from ..controllers import main, onboard


class TestExamCommon(common.TransactionCase):
    def setUp(self):
        super(TestExamCommon, self).setUp()
        self.op_marksheet_line = self.env['op.marksheet.line']
        self.res_company = self.env['res.company']
        self.marksheet_line_progress_wizard = \
            self.env['marksheet.line.progress.wizard']
        self.op_exam_session = self.env['op.exam.session']


class ExamContollerTests(TransactionCase):

    def setUp(self):
        super().setUp()
        self.examcontroller = onboard.OnboardingController()


class TestExamController(ExamContollerTests):

    def setUp(self):
        super(TestExamController, self).setUp()

    # def test_case_exam_onboard(self):
    #     self.examcontroller = onboard.OnboardingController()
    #
    #     with MockRequest(self.env):
    #         self.onboard = self.examcontroller.\
    #             openeducat_exam_onboarding_panel()


class TestExamMainController(ExamContollerTests):

    def setUp(self):
        super(TestExamMainController, self).setUp()

    def test_exam_main(self):
        self.exammaincontroller = main.Exam()

        with MockRequest(self.env):
            self.main = self.exammaincontroller.get_exams()
            self.main = self.exammaincontroller.get_exam_chart_details()
            self.main = self.exammaincontroller.get_exam_sessions()
            self.main = self.exammaincontroller.get_subject_details(session_id=2)


class TestExamMainPortal(ExamContollerTests):

    def setUp(self):
        super(TestExamMainPortal, self).setUp()

    def test_exam_portal(self):
        self.examportal = main.ExamPortal()
        with MockRequest(self.env):
            self.main = self.examportal._prepare_portal_layout_values()
            self.main = self.examportal.check_exam_access(2)


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        stud = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        stud.login = 'student'
        parent = self.env['res.users'].search(
            [('login', '=', 'parent@openeducat.com')])
        parent.login = 'parent'

    def test_student_exam(self):
        self.start_tour("/", "student_exam", login="student")
        self.start_tour("/", "student_exam", login="parent")

    def test_student_exam_data(self):
        self.start_tour("/", "student_exam_data", login="student")
        self.start_tour("/", "student_exam_data", login="parent")
