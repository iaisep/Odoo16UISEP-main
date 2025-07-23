# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo.tests import common


class TestDashboardCommon(common.TransactionCase):

    def setUp(self):
        super(TestDashboardCommon, self).setUp()
        self.main_dashboard = self.env["dashboard_pro.main_dashboard"]
        self.item_action = self.env["pro_dashboard_pro.item_action"]
        self.to_do_list = self.env["to_do.list"]
        self.element = self.env["dashboard_pro.element"]
        self.element_action = self.env["dashboard_pro.element_action"]
