# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.tests import TransactionCase, common


class TestParentCommon(common.TransactionCase):
    def setUp(self):
        super(TestParentCommon, self).setUp()
        self.op_parent = self.env['op.parent']
        self.res_company = self.env['res.company']


class ParentController(TransactionCase):

    def setUp(self):
        super().setUp()


class TestParentController(ParentController):

    def setUp(self):
        super(TestParentController, self).setUp()

    # def test_case_1_onboard(self):
    #     self.parent_onboard_controller = onboard.OnboardingController()
    #
    #     with MockRequest(self.env):
    #         self.parent_onboard = self.parent_onboard_controller. \
    #             openeducat_parent_onboarding_panel()


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        parent = self.env['res.users'].search([('login', '=', 'parent@openeducat.com')])
        parent.login = "parent"

    def test_01_my_child(self):
        self.start_tour("/", "test_my_child", login="parent")
