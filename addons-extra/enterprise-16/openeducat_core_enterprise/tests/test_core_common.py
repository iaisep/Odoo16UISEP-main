# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.http import request
from odoo.tests import TransactionCase, common

from odoo.addons.website.tools import MockRequest

from ..controllers import main


class TestCoreCommon(common.TransactionCase):
    def setUp(self):
        super(TestCoreCommon, self).setUp()
        self.op_subject = self.env['op.subject']
        self.res_company = self.env['res.company']
        self.op_faculty = self.env['op.faculty']
        self.op_course = self.env['op.course']
        self.op_batch = self.env['op.batch']
        self.wizard_badge = self.env['op.badge.student.wizard']
        self.res_users = self.env['res.users']


class CoreController(TransactionCase):

    def setUp(self):
        super(CoreController, self).setUp()


class TestCoreController(CoreController):

    def setUp(self):
        super(TestCoreController, self).setUp()

    # def test_case_1_onboard(self):
    #     self.onboard_controller = onboard.OnboardingController()
    #
    #     with MockRequest(self.env):
    #         self.core_onboard = self.onboard_controller.\
    #             openeducat_core_enterprise_onboarding_panel()

    def test_case_1_main(self):
        self.core_main_controller = main.StudentPortal()
        with MockRequest(self.env):
            student = request.env.user
            self.main_controller = self.\
                core_main_controller.check_access_role(student)
            self.main_controller = self.\
                core_main_controller.get_student(student_id=None)

    def test_case_2_main_OpenEduCatController(self):
        self.core_main_controller = main.OpenEduCatController()
        self.subject_regi_controller = main.SubjectRegistrationPortal()

        with MockRequest(self.env):
            self.main_controller = self.\
                core_main_controller.fetch_openeducat_batches()
            self.main_controller = self.\
                core_main_controller.compute_openeducat_batch_graph(batch_id=None)
            course_id = self.env.ref('openeducat_core.op_course_2')
            self.main_controller = self.\
                subject_regi_controller.get_course_data(course_id=str(course_id.id))


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        stud = self.env['res.users'].search([('login', '=', 'student@openeducat.com')])
        stud.login = 'student'

    def test_01_student_profile(self):
        self.start_tour("/", "test_student_profile", login="student")

    def test_03_subject_registration(self):
        self.start_tour("/", "test_subject_registration", login="student")
