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


class TestAssignmentCommon(common.TransactionCase):
    def setUp(self):
        super(TestAssignmentCommon, self).setUp()
        self.op_assignment = self.env['op.assignment']
        self.op_assignment_subline = self.env['op.assignment.sub.line']
        self.op_assignment_type = self.env['grading.assignment.type']
        self.op_progression_assignment = self.env['op.student.progression']
        self.op_company = self.env['res.company']
        self.op_progression_wizard = self.env['assignment.progress.wizard']


class AssignmentContollerTests(TransactionCase):

    def setUp(self):
        super().setUp()
        self.AssignmentController = onboard.OnboardingController()


# class TestAssignmentController(AssignmentContollerTests):
#
#     def setUp(self):
#         super(TestAssignmentController, self).setUp()
#
#     def test_case_assignment_onboard(self):
#         self.AssignmentController = onboard.OnboardingController()
#         with MockRequest(self.env):
#             self.cookies = self.AssignmentController. \
#                 openeducat_assignment_onboarding_panel()


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

    def test_01_assignment2(self):
        self.start_tour("/", 'test_assignment', login="student")
        self.start_tour("/", 'test_assignment', login="parent")

    def test_02_assignment_submit2(self):
        self.start_tour("/", 'test_assignment_submit', login="student")

    #  there is Redirected at the Controller Action
    # def test_04_assignment_create(self):
    #     self.start_tour("/", "test_assignment_submit_create", login="student")
