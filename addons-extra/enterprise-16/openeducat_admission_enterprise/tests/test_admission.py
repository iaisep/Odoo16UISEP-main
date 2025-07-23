# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_admission_common import TestAdmissionCommon


class TestAdmission(TestAdmissionCommon):

    def setUp(self):
        super(TestAdmission, self).setUp()

    def test_case_1_admissions(self):
        admissions = self.op_admission.search([])

        for admission in admissions:
            logging.info('%s :    %s' % (admission.company_id, admission.name))


class TestAdmissionregister(TestAdmissionCommon):

    def setUp(self):
        super(TestAdmissionregister, self).setUp()

    def test_case_1_register(self):
        register = self.op_register.search([])

        for registers in register:
            logging.info('Comapny Name : %s :' % (registers.company_id.name))
            registers.action_onboarding_admission_register_layout()


class TestComapny(TestAdmissionCommon):

    def setUp(self):
        super(TestComapny, self).setUp()

    def test_case_1_company(self):
        company = self.res_company.search([])

        logging.info(
            'State of the onboarding admission layout step : %s :  ' % (
                company.openeducat_admission_onboard_panel))
        logging.info('State of the onboarding admission layout step : %s :  ' % (
            company.onboarding_admission_register_layout_state))

        company.action_close_admission_panel_onboarding()
        company.action_onboarding_admission_register_layout()
        company.update_admission_onboarding_state()
