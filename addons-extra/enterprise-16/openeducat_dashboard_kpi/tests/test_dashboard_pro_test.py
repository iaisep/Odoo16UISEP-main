# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from .test_dashboard_pro_common import TestDashboardCommon


class TestMainDashboard(TestDashboardCommon):
    def setUp(self):
        super(TestMainDashboard, self).setUp()

    def test_case_1_main_dashboard(self):
        dashboards = self.main_dashboard.search([])
        element = self.element.search([("id", "=", 8)])

        for dash in dashboards:
            dash.get_dashboard_values_to(dashboard_id=1)
            dash.get_theme_data(theme_id=[1])
            dash.get_element(item_list=[1, 2, 3, 4, 5, 6, 7, 8], dashboard_id=1)
            dash.change_dashboard_theme_func(theme_id=1)
            dash.changing_date(dashboard_id=1)
            dash.element_export(element_id=6)
            dash.get_element_data(dash.dashboard_item_ids.browse(int("6")))
            dash.get_item_data(dashboard_rec=element)


class TestItemAction(TestDashboardCommon):
    def setUp(self):
        super(TestItemAction, self).setUp()
