# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from .test_dashboard_pro_common import TestDashboardCommon


class TestToDoList(TestDashboardCommon):
    def setUp(self):
        super(TestToDoList, self).setUp()

    def test_case_1_to_do_list(self):
        lists = self.to_do_list.search([])

        for li in lists:
            li.to_do_list_delete_func()
            li.to_do_list_state_change_func(state="to_do")


class TestElement(TestDashboardCommon):
    def setUp(self):
        super(TestElement, self).setUp()

    def test_case_1_element(self):
        eles = self.element.search([])
        element = self.element.search([("id", "=", 8)])

        for el in eles:
            el.onchange_state_layout_state()
            el.onchange_state_layout_state_1()
            el.update_form_view()
            el.create(values={"type_of_element": "to_do"})
            el.update_add_link_preview()
            el._compute_get_data_calculation()
            el.getting_data_of_model(
                model_name="res.country",
                domain='[["id","<",10]]',
                func="search_count",
                dashboard_rec="openeducat_dashboard_kpi.element(3,)",
            )
            el._compute_chart_group_type_fun()
            el.empty_sub_group_by()
            el._compute_to_do_list_total_count()
            el._compute_todo_list_element_info_func()
            el._compute_list_element_info_func()
            el.set_color_palette()
            el.list_info_sub_func(dashboard_rec=element)
            el.convert_into_proper_domain(domain=False, dashboard_rec=element)
            el._compute_kpi_info_func()
            el.filter_previous_data_func(dashboard_rec=element)
            el.record_empty_func_2()
            el.domain_previous_func(
                domain=False, start_date=False, end_date=False, date_filter_field=False
            )
            el._compute_data_calculation_func_1()
            el.getting_data_of_model_2(
                model_name=False, domain=False, func=False, dashboard_rec=False
            )
            el.domain_conversion_func(domain_2=False, dashboard_rec=element)
            el._compute_chart_group_type_func()
            el.get_sorted_month(display_format="")
            el.create_time_pattern_func(
                "2020-01-01 00:00:00", "2020-12-31 00:00:00", "day", "date"
            )
            el.format_label(
                value=None,
                ftype="date",
                display_format="",
                tz_convert="",
                locale="en_US",
            )
            el.domain_onchange_func()
            el.domain_onchange_func_2()
            el.gropu_data_sort_func(
                data="",
                field_type="",
                chart_group_field="",
                sorting_selection="",
                chart_sub_field_date="",
            )
            el.dashboard_element_theme_func()
            el.dark_color_generator(color="#54654", opacity="")
            el.date_filter_func()
            el.date_filter_func_2()
            el._compute_chart_data_func()
            el.get_start_end_date(
                model_name=False,
                chart_domain=False,
                chart_groupby_relation_field=False,
                ttype=False,
                goal_domain=[],
            )


class TestElementAction(TestDashboardCommon):
    def setUp(self):
        super(TestElementAction, self).setUp()

    def test_case_1_element_action(self):
        actions = self.element_action.search([])

        for action in actions:
            action.get_item_action_type()
            action.check_date_group_by()
