# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo.tests import TransactionCase, common


class TestAdmissionCommon(common.TransactionCase):
    def setUp(self):
        super(TestAdmissionCommon, self).setUp()
        self.op_student = self.env['op.student.fees.details']
        self.res_company = self.env['res.company']
        self.op_register = self.env['op.admission.register']
        self.op_admission = self.env['op.admission']


class AdmissionController(TransactionCase):

    def setUp(self):
        super().setUp()


class TestAdmissionController(AdmissionController):

    def setUp(self):
        super(TestAdmissionController, self).setUp()

    # def test_case_1_onboard(self):
    #     self.admission_controller = OnboardingController()
    #
    #     with MockRequest(self.env):
    #         self.onboard = self.admission_controller.openeducat_admission_onboarding()
