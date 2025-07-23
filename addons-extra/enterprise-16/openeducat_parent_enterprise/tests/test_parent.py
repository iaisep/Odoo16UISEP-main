# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_parent_common import TestParentCommon


class TestParent(TestParentCommon):

    def setUp(self):
        super(TestParent, self).setUp()

    def test_case_1_company(self):
        parent = self.op_parent.search([])
        logging.info('Details of Core Company')
        logging.info('company : %s :  ' % (parent.company_id))
        parent.action_onboarding_parent_layout()


class TestComapny(TestParentCommon):

    def setUp(self):
        super(TestComapny, self).setUp()

    def test_case_1_company(self):
        company = self.res_company.search([])
        logging.info('Details of Parent Company')
        logging.info(
            'openeducat_parent_onboard_panel : %s :  ' % (
                company.openeducat_parent_onboard_panel))
        logging.info('core_onboarding_parent_layout_state : %s :  ' % (
            company.core_onboarding_parent_layout_state))

        company.action_close_parent_panel_onboarding()
        company.action_onboarding_parent_layout()
        company.update_parent_onboarding_state()
