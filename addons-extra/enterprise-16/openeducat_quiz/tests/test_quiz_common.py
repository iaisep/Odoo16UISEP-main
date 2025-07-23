# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.tests import TransactionCase, common

from ..controllers import onboard


class TestQuizCommon(common.TransactionCase):
    def setUp(self):
        super(TestQuizCommon, self).setUp()
        self.op_category = self.env['op.quiz.category']
        self.op_grade = self.env['op.answer.grade']
        self.op_que_bank_type = self.env['op.question.bank.type']
        self.op_que_bank = self.env['op.question.bank']
        self.op_que_bank_line = self.env['op.question.bank.line']
        self.quiz_onboard = self.env['res.company']
        self.op_question_wizard = self.env['op.question.wizard']
        self.op_quiz_result = self.env['op.quiz.result']
        self.op_quiz_result_line = self.env['op.quiz.result.line']
        self.op_quiz = self.env['op.quiz']


class QuizContollerTests(TransactionCase):

    def setUp(self):
        super().setUp()
        self.quizcontroller = onboard.OnboardingController()


class TestQuizController(QuizContollerTests):

    def setUp(self):
        super(TestQuizController, self).setUp()

    # def test_quiz_onboard(self):
    #     with MockRequest(self.env):
    #         self.onboard = self.quizcontroller.\
    #             openeducat_quiz_onboarding_panel()


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

    def test_01_quiz_rules(self):
        self.start_tour("/", "quiz_rules", login="student")
        # self.start_tour("/", "quiz_rules", login="parent")

    def test_online_exam(self):
        self.start_tour("/", "online_exam", login="student")
        # self.start_tour("/", "online_exam", login="parent")
