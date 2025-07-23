# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import datetime
import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

from ..lib.filter_function import generate_date


class DashboardProTheme(models.Model):
    _name = "dashboard_pro.theme"
    _description = "Theme Of Dashboard"

    name = fields.Char(string="Name")
    dashboard_theme_primary_color = fields.Char(
        default="#000000,0.99", string="Primary Color"
    )
    dashboard_theme_secondary_color = fields.Char(
        default="#000000,0.99", string="Secondary Color"
    )
    dashboard_theme_font_color = fields.Char(
        default="#000000,0.99", string="Font Color"
    )


class DashboardProMainDashboard(models.Model):
    _name = "dashboard_pro.main_dashboard"
    _description = "Main Dashboard Model And Objects"

    name = fields.Char(string="Dashboard Name", required=True)
    dashboard_item_ids = fields.One2many(
        "dashboard_pro.element", "dashboard_pro_dashboard_id", string="Dashboard Items"
    )
    menu_name_dashboard = fields.Char(string="Menu Name")
    dashboard_top_menu_id = fields.Many2one(
        "ir.ui.menu", domain="[('parent_id','=',False)]", string="Show Under Menu"
    )
    starting_date_dashboard = fields.Datetime(string="Start Date")
    ending_date_dashboard = fields.Datetime(string="End Date")
    client_action = fields.Many2one("ir.actions.client")
    date_domain_fields = fields.Selection(
        [
            ("none", "All Time"),
            ("last_day", "Today"),
            ("this_week", "This Week"),
            ("this_month", "This Month"),
            ("this_quarter", "This Quarter"),
            ("this_year", "This Year"),
            ("next_day", "Next Day"),
            ("next_week", "Next Week"),
            ("next_month", "Next Month"),
            ("next_quarter", "Next Quarter"),
            ("next_year", "Next Year"),
            ("lastp_day", "Last Day"),
            ("lastp_week", "Last Week"),
            ("lastp_month", "Last Month"),
            ("lastp_quarter", "Last Quarter"),
            ("lastp_year", "Last Year"),
            ("last_week", "Last 7 days"),
            ("last_month", "Last 30 days"),
            ("last_quarter", "Last 90 days"),
            ("last_year", "Last 365 days"),
            ("last_custom", "Custom Filter"),
        ],
        default="none",
        string="Default Date Filter",
    )

    dashboard_menu_id = fields.Many2one("ir.ui.menu")
    dashboard_theme_id = fields.Many2one(
        "dashboard_pro.theme",
        string="Dashboard Theme",
        default=lambda self: self.env["dashboard_pro.theme"].search([], limit=1),
    )
    dashboard_state = fields.Char()
    dashboard_active = fields.Boolean(string="Active", default=True)
    dashboard_group_access = fields.Many2many("res.groups", string="Group Access")

    grid_configuration = fields.Char("Item Configurations")
    dashboard_default_template = fields.Many2one(
        "dashboard_pro.dashboard_template",
        default=lambda self: self.env.ref("openeducat_dashboard_kpi.blank", False),
        string="Dashboard Template",
    )

    interval_time = fields.Selection(
        [
            ("15000", "15 Seconds"),
            ("30000", "30 Seconds"),
            ("45000", "45 Seconds"),
            ("60000", "1 minute"),
            ("120000", "2 minute"),
            ("300000", "5 minute"),
            ("600000", "10 minute"),
        ],
        string="Update Interval Time",
        help="Update Interval for new items only",
    )
    dashboard_menu_sequence = fields.Integer(
        string="Menu Sequence",
        default=10,
        help="""Smallest sequence give high priority
        and Highest sequence give low priority""",
    )

    @api.onchange("date_domain_fields")
    def date_change_onchange_method(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.date_domain_fields
                and dashboard_rec.date_domain_fields != "last_custom"
            ):
                dashboard_rec.starting_date_dashboard = False
                dashboard_rec.ending_date_dashboard = False

    @api.model
    def get_dashboard_values_to(self, dashboard_id, item_domain=False):
        has_group_dashboard_manager = self.env.user.has_group(
            "openeducat_dashboard_kpi.dashboard_pro_group_manager"
        )
        dashboard_data = {
            "name": self.browse(dashboard_id).name,
            "dashboard_manager": has_group_dashboard_manager,
            "dashboard_list": self.search_read([], ["id", "name"]),
            "all_theme_data": self.env["dashboard_pro.theme"].search_read(
                [],
                [
                    "id",
                    "name",
                    "dashboard_theme_primary_color",
                    "dashboard_theme_font_color",
                    "dashboard_theme_secondary_color",
                ],
            ),
            "starting_date_dashboard": self._context.get("DateFilterStartDate", False)
            or self.browse(dashboard_id).starting_date_dashboard,
            "ending_date_dashboard": self._context.get("DateFilterEndDate", False)
            or self.browse(dashboard_id).ending_date_dashboard,
            "date_domain_fields": self._context.get("DateFilterSelection", False)
            or self.browse(dashboard_id).date_domain_fields,
            "grid_configuration": self.browse(dashboard_id).grid_configuration,
            "interval_time": self.browse(dashboard_id).interval_time,
        }
        if len(self.browse(dashboard_id).dashboard_theme_id) < 1:
            theme_data = False
        else:
            theme_data = self.get_theme_data(
                self.browse(dashboard_id).dashboard_theme_id.ids
            )

        dashboard_data["theme_data"] = json.dumps(theme_data)

        if len(self.browse(dashboard_id).dashboard_item_ids) < 1:
            dashboard_data["element_data"] = False
        else:
            if item_domain:
                try:
                    items = self.get_element(
                        self.dashboard_item_ids.search(
                            [["dashboard_pro_dashboard_id", "=", dashboard_id]]
                            + item_domain
                        ).ids,
                        dashboard_id,
                    )
                except Exception:
                    items = self.get_element(
                        self.browse(dashboard_id).dashboard_item_ids.ids, dashboard_id
                    )
                    dashboard_data["element_data"] = items
                    return dashboard_data
            else:
                items = self.get_element(
                    self.browse(dashboard_id).dashboard_item_ids.ids, dashboard_id
                )

            dashboard_data["element_data"] = items
        return dashboard_data

    @api.model
    def get_theme_data(self, theme_id):
        theme_model = self.env["dashboard_pro.theme"].browse(theme_id)
        theme = {
            "id": theme_model.id,
            "name": theme_model.name,
            "dashboard_theme_primary_color": theme_model.dashboard_theme_primary_color,
            "dashboard_theme_secondary_color":
                theme_model.dashboard_theme_secondary_color,
            "dashboard_theme_font_color": theme_model.dashboard_theme_font_color,
        }
        return theme

    @api.model
    def get_element(self, item_list, dashboard_id):
        self = self.changing_date(dashboard_id)
        elements = {}
        item_model = self.env["dashboard_pro.element"]
        for element_id in item_list:
            item = self.get_item_data(item_model.browse(element_id))
            elements[item["id"]] = item
        return elements

    def unlink(self):
        if self.env.ref("openeducat_dashboard_kpi.default_dashboard").id in self.ids:
            raise ValidationError(_("Default Dashboard can't be deleted."))
        else:
            for dashboard_rec in self:
                dashboard_rec.client_action.sudo().unlink()
                dashboard_rec.dashboard_menu_id.sudo().unlink()
                dashboard_rec.dashboard_item_ids.unlink()
        res = super(DashboardProMainDashboard, self).unlink()
        return res

    def change_dashboard_theme_func(self, theme_id):
        theme_model = self.env["dashboard_pro.theme"].search([("id", "=", theme_id)])
        self.dashboard_theme_id = theme_model

        return theme_model.name

    def changing_date(self, dashboard_id):
        if self._context.get("DateFilterSelection", False):
            date_domain_fields = self._context["DateFilterSelection"]
            if date_domain_fields == "last_custom":
                self = self.with_context(
                    DateFilterStartDate=fields.datetime.strptime(
                        self._context["DateFilterStartDate"], "%Y-%m-%dT%H:%M:%S.%fz"
                    )
                )
                self = self.with_context(
                    DateFilterEndDate=fields.datetime.strptime(
                        self._context["DateFilterEndDate"], "%Y-%m-%dT%H:%M:%S.%fz"
                    )
                )

        else:
            date_domain_fields = self.browse(dashboard_id).date_domain_fields
            self = self.with_context(
                DateFilterStartDate=self.browse(dashboard_id).starting_date_dashboard
            )
            self = self.with_context(
                DateFilterEndDate=self.browse(dashboard_id).ending_date_dashboard
            )
            self = self.with_context(DateFilterSelection=date_domain_fields)

        if date_domain_fields not in ["last_custom", "none"]:
            filter_date_value = generate_date(date_domain_fields)
            self = self.with_context(
                DateFilterStartDate=filter_date_value["selected_start_date"]
            )
            self = self.with_context(
                DateFilterEndDate=filter_date_value["selected_end_date"]
            )

        return self

    def element_export(self, element_id):

        return {
            "file_format": "dashboard_pro_item_export",
            "item": self.get_element_data(
                self.dashboard_item_ids.browse(int(element_id))
            ),
        }

    def write(self, vals):
        if (
            vals.get("date_domain_fields", False)
            and vals.get("date_domain_fields") != "last_custom"
        ):
            vals.update(
                {"starting_date_dashboard": False, "ending_date_dashboard": False}
            )
        record = super(DashboardProMainDashboard, self).write(vals)
        for dashboard_rec in self:
            if "menu_name_dashboard" in vals:
                if (
                    self.env.ref("openeducat_dashboard_kpi.default_dashboard")
                    and self.env.ref("openeducat_dashboard_kpi.default_dashboard").
                        sudo().id == dashboard_rec.id):
                    if self.env.ref("openeducat_dashboard_kpi.dashboard_menu", False):
                        self.env.ref("openeducat_dashboard_kpi.dashboard_menu").\
                            sudo().name = vals[
                            "menu_name_dashboard"
                        ]
                else:
                    dashboard_rec.dashboard_menu_id.sudo().name = vals[
                        "menu_name_dashboard"
                    ]

            if "dashboard_group_access" in vals:
                if (
                    self.env.ref("openeducat_dashboard_kpi.default_dashboard").id
                    == dashboard_rec.id
                ):
                    if self.env.ref("openeducat_dashboard_kpi.dashboard_menu", False):
                        self.env.ref("openeducat_dashboard_kpi.dashboard_menu").\
                            groups_id = vals["dashboard_group_access"]
                else:
                    dashboard_rec.dashboard_menu_id.sudo().groups_id = vals[
                        "dashboard_group_access"
                    ]

            if "dashboard_active" in vals and dashboard_rec.dashboard_menu_id:
                dashboard_rec.dashboard_menu_id.sudo().active = vals["dashboard_active"]

            if "dashboard_top_menu_id" in vals:
                dashboard_rec.dashboard_menu_id.write(
                    {"parent_id": vals["dashboard_top_menu_id"]}
                )

            if "dashboard_menu_sequence" in vals:
                dashboard_rec.dashboard_menu_id.sudo().sequence = vals[
                    "dashboard_menu_sequence"
                ]

        return record

    def get_element_data(self, dashboard_rec):
        chart_data_calculation_field = []
        chart_data_calculation_field_2 = []
        for res in dashboard_rec.chart_data_calculation_field:
            chart_data_calculation_field.append(res.name)
        for res in dashboard_rec.chart_data_calculation_field_2:
            chart_data_calculation_field_2.append(res.name)

        list_data_grouping = []
        for res in dashboard_rec.list_data_grouping:
            list_data_grouping.append(res.name)

        goal_lines = []
        for res in dashboard_rec.goal_lines:
            goal_line = {
                "goal_date": datetime.datetime.strftime(res.goal_date, "%Y-%m-%d"),
                "goal_value": res.goal_value,
            }
            goal_lines.append(goal_line)

        to_do_list_line = []
        for res in dashboard_rec.to_do_list_line:
            to_do_line = {
                "id": res.id,
                "name": res.name,
                "sequence": res.sequence,
                "to_do_state": res.to_do_state,
            }
            to_do_list_line.append(to_do_line)

        action_lines = []
        for res in dashboard_rec.action_lines:
            action_line = {
                "item_action_field": res.item_action_field.name,
                "item_action_date_groupby": res.item_action_date_groupby,
                "chart_type": res.chart_type,
                "sorting_selection_by_field": res.sorting_selection_by_field.name,
                "sorting_selection": res.sorting_selection,
                "record_limit": res.record_limit,
                "sequence": res.sequence,
            }
            action_lines.append(action_line)

        list_view_field = []
        for res in dashboard_rec.list_fields_data:
            list_view_field.append(res.name)
        item = {
            "name": dashboard_rec.name
            if dashboard_rec.name
            else dashboard_rec.model_id.name
            if dashboard_rec.model_id
            else "Name",
            "background_color": dashboard_rec.background_color,
            "font_color": dashboard_rec.font_color,
            "domain": dashboard_rec.domain,
            "icon": dashboard_rec.icon,
            "id": dashboard_rec.id,
            "add_text_main_content": dashboard_rec.add_text_main_content,
            "add_text_custom_bold": dashboard_rec.add_text_custom_bold,
            "add_text_align": dashboard_rec.add_text_align,
            "add_text_custom_italic": dashboard_rec.add_text_custom_italic,
            "add_text_custom_font_size": dashboard_rec.add_text_custom_font_size,
            "add_text_font_style": dashboard_rec.add_text_font_style,
            "type_of_element": dashboard_rec.type_of_element,
            "chart_theme_selection": dashboard_rec.chart_theme_selection,
            "group_chart_field": dashboard_rec.group_chart_field,
            "group_chart_relation": dashboard_rec.group_chart_relation.name,
            "model_id": dashboard_rec.model_name,
            "to_do_list_line": to_do_list_line,
            "add_link_content": dashboard_rec.add_link_content,
            "add_link_title": dashboard_rec.add_link_title,
            "add_divider_line": dashboard_rec.add_divider_line,
            "add_image_image": dashboard_rec.add_image_image.decode("utf-8")
            if dashboard_rec.add_image_image
            else False,
            "data_calculation_value": dashboard_rec.data_calculation_value,
            "layout": dashboard_rec.layout,
            "starting_date_kpi_2": dashboard_rec.starting_date_kpi_2.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )
            if dashboard_rec.starting_date_kpi_2
            else False,
            "ending_date_kpi_2": dashboard_rec.ending_date_kpi_2.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )
            if dashboard_rec.ending_date_kpi_2
            else False,
            "previous_data_field": dashboard_rec.previous_data_field,
            "selection_icon_field": dashboard_rec.selection_icon_field,
            "default_icon": dashboard_rec.default_icon,
            "default_icon_color": dashboard_rec.default_icon_color,
            "chart_group_field": dashboard_rec.chart_group_field,
            "date_filter_field": dashboard_rec.date_filter_field.name,
            "is_goal_enable": dashboard_rec.is_goal_enable,
            "goal_value_field": dashboard_rec.goal_value_field,
            "new_goal_lines": goal_lines,
            "date_domain_fields": dashboard_rec.date_domain_fields,
            "element_start_date": dashboard_rec.element_start_date.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )
            if dashboard_rec.element_start_date
            else False,
            "element_end_date": dashboard_rec.element_end_date.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )
            if dashboard_rec.element_end_date
            else False,
            "date_filter_selection_2": dashboard_rec.date_filter_selection_2,
            "filter_limit": dashboard_rec.filter_limit,
            "sorting_selection": dashboard_rec.sorting_selection,
            "unit": dashboard_rec.unit,
            "show_records": dashboard_rec.show_records,
            "unit_selection": dashboard_rec.unit_selection,
            "chart_unit": dashboard_rec.chart_unit,
            "bar_chart_stacked": dashboard_rec.bar_chart_stacked,
            "goal_line_field": dashboard_rec.goal_line_field,
            "actions": dashboard_rec.actions.xml_id if dashboard_rec.actions else False,
            "sorting_selection_by_field": dashboard_rec.sorting_selection_by_field.name,
            "store_field_data": dashboard_rec.store_field_data.name,
            "to_do_list_count": dashboard_rec.to_do_list_count,
            "json_todo_list_data": dashboard_rec.json_todo_list_data,
            "sub_group_chart_field": dashboard_rec.sub_group_chart_field,
            "chart_sub_field": dashboard_rec.chart_sub_field.name,
            "chart_sub_field_date": dashboard_rec.chart_sub_field_date,
            "data_calculation_type_chart": dashboard_rec.data_calculation_type_chart,
            "chart_data_calculation_field": chart_data_calculation_field,
            "chart_data_calculation_field_2": chart_data_calculation_field_2,
            "list_fields_data": list_view_field,
            "list_data_grouping": list_data_grouping,
            "list_view_type": dashboard_rec.list_view_type,
            "target_view": dashboard_rec.target_view,
            "time_of_comparation_2": dashboard_rec.time_of_comparation_2,
            "year_period_2": dashboard_rec.year_period_2,
            "domain_2": dashboard_rec.domain_2,
            "show_data_value": dashboard_rec.show_data_value,
            "update_element_data_time": dashboard_rec.update_element_data_time,
            "kpi_compare_field": dashboard_rec.kpi_compare_field,
            "new_action_lines": action_lines,
            "time_of_comparation": dashboard_rec.time_of_comparation,
            "year_period": dashboard_rec.year_period,
            "data_calculation_type": dashboard_rec.data_calculation_type,
            "store_field_data_2": dashboard_rec.store_field_data_2.name,
            "ir_model_field_2": dashboard_rec.ir_model_field_2.model,
            "date_filter_field_2": dashboard_rec.date_filter_field_2.name,
            "list_goal_field": dashboard_rec.list_goal_field.name,
        }
        return item

    @api.model
    def dashboard_export(self, dashboard_ids):
        dashboard_data_list = []
        dashboard_export_data = {}
        dashboard_ids = json.loads(dashboard_ids)
        for dashboard_id in dashboard_ids:
            dashboard_data = {
                "name": self.browse(dashboard_id).name,
                "menu_name_dashboard": self.browse(dashboard_id).menu_name_dashboard,
                "grid_configuration": self.browse(dashboard_id).grid_configuration,
                "interval_time": self.browse(dashboard_id).interval_time,
                "date_domain_fields": self.browse(dashboard_id).date_domain_fields,
                "starting_date_dashboard": self.browse(
                    dashboard_id
                ).starting_date_dashboard,
                "ending_date_dashboard": self.browse(
                    dashboard_id
                ).ending_date_dashboard,
            }
            if len(self.browse(dashboard_id).dashboard_item_ids) < 1:
                dashboard_data["element_data"] = False
            else:
                items = []
                for dashboard_rec in self.browse(dashboard_id).dashboard_item_ids:
                    item = self.get_element_data(dashboard_rec)
                    items.append(item)

                dashboard_data["element_data"] = items

            dashboard_data_list.append(dashboard_data)

            dashboard_export_data = {
                "file_format": "dashboard_pro_export_file",
                "dashboard_data": dashboard_data_list,
            }
        return dashboard_export_data

    @api.model
    def list_data_offset(self, dashboard_item_id, offset, dashboard_id):
        self = self.changing_date(dashboard_id)
        item = self.dashboard_item_ids.browse(dashboard_item_id)
        if int(offset["offset"]) < 0:
            offset["offset"] = int(offset["offset"]) + int(-(offset["offset"]))
        return item.next_offset_func(dashboard_item_id, offset)

    def get_item_data(self, dashboard_rec):
        if dashboard_rec.actions:
            action = {}
            action["name"] = dashboard_rec.actions.name
            action["type"] = dashboard_rec.actions.type
            action["res_model"] = dashboard_rec.actions.res_model
            action["views"] = dashboard_rec.actions.views
            action["view_mode"] = dashboard_rec.actions.view_mode
            action["target"] = "current"
        else:
            action = False

        for x_rec in dashboard_rec.to_do_list_line: # noqa
            if dashboard_rec.type_of_element == "to_do":
                json_todo_list_data = {
                    "data_rows": [],
                    "model": "to_do.list",
                    "label": ["Done", "To-Do List", ""],
                }
                for i in dashboard_rec.to_do_list_line:
                    data_row = {"id": i.id, "data": [], "state": ""}
                    if i.to_do_state == "to_do" or i.to_do_state == "done":
                        data_row["state"] = i.to_do_state
                        data_row["data"].append(i.name)

                    json_todo_list_data["data_rows"].append(data_row)

                dashboard_rec.json_todo_list_data = json.dumps(json_todo_list_data)
            else:
                dashboard_rec.json_todo_list_data = False
        item = {
            "name": dashboard_rec.name
            if dashboard_rec.name
            else dashboard_rec.model_id.name
            if dashboard_rec.model_id
            else "Name",
            "background_color": dashboard_rec.background_color,
            "font_color": dashboard_rec.font_color,
            "domain": dashboard_rec.convert_into_proper_domain(
                dashboard_rec.domain, dashboard_rec
            ),
            "dashboard_id": dashboard_rec.dashboard_pro_dashboard_id.id,
            "icon": dashboard_rec.icon,
            "model_id": dashboard_rec.model_id.id,
            "group_chart_field": dashboard_rec.group_chart_field,
            "group_chart_relation": dashboard_rec.group_chart_relation.id,
            "chart_relation_groupby_name": dashboard_rec.group_chart_relation.name,
            "chart_group_field": dashboard_rec.chart_group_field,
            "model_name": dashboard_rec.model_name,
            "model_display_name": dashboard_rec.model_id.name,
            "data_calculation_type": dashboard_rec.data_calculation_type,
            "data_calculation_value": dashboard_rec.data_calculation_value,
            "id": dashboard_rec.id,
            "layout": dashboard_rec.layout,
            "bar_chart_stacked": dashboard_rec.bar_chart_stacked,
            "semi_circle_chart": dashboard_rec.semi_circle_chart,
            "list_view_type": dashboard_rec.list_view_type,
            "list_data_grouping": dashboard_rec.list_data_grouping.ids
            if dashboard_rec.list_data_grouping
            else False,
            "previous_data_field": dashboard_rec.previous_data_field,
            "kpi_data": dashboard_rec.kpi_data,
            "default_icon_color": dashboard_rec.default_icon_color,
            "type_of_element": dashboard_rec.type_of_element,
            "chart_theme_selection": dashboard_rec.chart_theme_selection,
            "target_view": dashboard_rec.target_view,
            "date_domain_fields": dashboard_rec.date_domain_fields,
            "show_data_value": dashboard_rec.show_data_value,
            "add_text_main_content": dashboard_rec.add_text_main_content,
            "add_text_custom_bold": dashboard_rec.add_text_custom_bold,
            "add_text_align": dashboard_rec.add_text_align,
            "add_text_custom_italic": dashboard_rec.add_text_custom_italic,
            "add_text_custom_font_size": dashboard_rec.add_text_custom_font_size,
            "add_text_font_style": dashboard_rec.add_text_font_style,
            "add_divider_line": dashboard_rec.add_divider_line,
            "update_element_data_time": dashboard_rec.update_element_data_time,
            "store_field_data": dashboard_rec.store_field_data.id
            if dashboard_rec.store_field_data
            else False,
            "chart_data": dashboard_rec.chart_data,
            "add_link_content": dashboard_rec.add_link_content,
            "add_link_title": dashboard_rec.add_link_title,
            "add_image_image": dashboard_rec.add_image_image,
            "json_list_data": dashboard_rec.json_list_data,
            "to_do_list_line": dashboard_rec.to_do_list_line,
            "to_do_list_count": dashboard_rec.to_do_list_count,
            "json_todo_list_data": dashboard_rec.json_todo_list_data,
            "data_calculation_type_chart": dashboard_rec.data_calculation_type_chart,
            "state_layout_state": dashboard_rec.state_layout_state,
            "state_layout_state_1": dashboard_rec.state_layout_state_1,
            "selection_icon_field": dashboard_rec.selection_icon_field,
            "default_icon": dashboard_rec.default_icon,
            "is_goal_enable": dashboard_rec.is_goal_enable,
            "ir_model_field_2": dashboard_rec.ir_model_field_2.id,
            "store_field_data_2": dashboard_rec.store_field_data_2.id,
            "kpi_compare_field": dashboard_rec.kpi_compare_field,
            "show_records": dashboard_rec.show_records,
            "sequence": 0,
            "max_sequnce": len(dashboard_rec.action_lines)
            if dashboard_rec.action_lines
            else False,
            "action": action,
        }
        return item

    def import_item(self, dashboard_id, **kwargs):
        file = kwargs.get("file", False)
        dashboard_file_read = json.loads(file)

        if (
            "file_format" in dashboard_file_read
            and dashboard_file_read["file_format"] == "dashboard_pro_item_export"
        ):
            item = dashboard_file_read["item"]
        else:
            raise ValidationError(
                _(
                    """Current Json File is not properly formatted
                    according to Dashboard pro Model."""
                )
            )

        item["dashboard_pro_dashboard_id"] = int(dashboard_id)
        self.create_element(item)

        return "Success"

    @api.model_create_multi
    def create(self, vals):
        record = super(DashboardProMainDashboard, self).create(vals)
        for rec in vals:

            if "dashboard_top_menu_id" in rec and "menu_name_dashboard" in rec:
                action_id = {
                    "name": rec["menu_name_dashboard"] + " Action",
                    "res_model": "dashboard_pro.main_dashboard",
                    "tag": "openeducat_dashboard_kpi",
                    "params": {"dashboard_id": record.id},
                }
                record.client_action = (
                    self.env["ir.actions.client"].sudo().create(action_id)
                )

                record.dashboard_menu_id = (
                    self.env["ir.ui.menu"]
                    .sudo()
                    .create(
                        {
                            "name": rec["menu_name_dashboard"],
                            "active": rec.get("dashboard_active", True),
                            "parent_id": rec["dashboard_top_menu_id"],
                            "action": "ir.actions.client," + str(
                                record.client_action.id),
                            "groups_id": rec.get("dashboard_group_access", False),
                            "sequence": rec.get("dashboard_menu_sequence", 10),
                        }
                    )
                )

            record.dashboard_theme_id = self.env. \
                ref("openeducat_dashboard_kpi.demo_dashboard_theme_1")

            if (
                record.dashboard_default_template
                and record.dashboard_default_template.item_count
            ):
                grid_configuration = {}
                template_data = json.loads(
                    record.dashboard_default_template.grid_configuration
                )
                for element_data in template_data:
                    dashboard_element = self.env.ref(element_data["element_id"]).copy(
                        {"dashboard_pro_dashboard_id": record.id}
                    )
                    grid_configuration[dashboard_element.id] = element_data["data"]
                record.grid_configuration = json.dumps(grid_configuration)
        return record

    @api.model
    def import_dashboard(self, file):
        dashboard_file_read = json.loads(file)

        if (
            "file_format" in dashboard_file_read
            and dashboard_file_read["file_format"] == "dashboard_pro_export_file"
        ):
            dashboard_data = dashboard_file_read["dashboard_data"]
        else:
            raise ValidationError(
                _(
                    """Current Json File is not properly
                    formatted according to Dashboard pro Model."""
                )
            )

        dashboard_key = ["name", "menu_name_dashboard", "grid_configuration"]
        dashboard_item_key = [
            "model_id",
            "chart_data_calculation_field",
            "list_fields_data",
            "to_do_list_line",
            "store_field_data",
            "group_chart_relation",
            "id",
        ]

        for data in dashboard_data:
            if not all(key in data for key in dashboard_key):
                raise ValidationError(
                    _(
                        """Current Json File is not properly
                        formatted according to Dashboard pro Model."""
                    )
                )
            vals = {
                "name": data["name"],
                "menu_name_dashboard": data["menu_name_dashboard"],
                "dashboard_top_menu_id": self.env.ref(
                    "dashboard_pro.board_menu_root"
                ).id,
                "dashboard_active": True,
                "grid_configuration": data["grid_configuration"],
                "dashboard_default_template": self.env.ref(
                    "openeducat_dashboard_kpi.blank"
                ).id,
                "dashboard_group_access": False,
                "interval_time": data["interval_time"],
                "date_domain_fields": data["date_domain_fields"],
                "starting_date_dashboard": data["starting_date_dashboard"],
                "ending_date_dashboard": data["ending_date_dashboard"],
            }
            dashboard_id = self.create(vals)

            if data["grid_configuration"]:
                grid_configuration = eval(data["grid_configuration"])
            grid_stack_config = {}

            item_ids = []
            item_new_ids = []
            if data["element_data"]:
                skiped = 0
                for item in data["element_data"]:
                    if not all(key in item for key in dashboard_item_key):
                        raise ValidationError(
                            _(
                                """Current Json File is not properly
                                 formatted according to Dashboard pro Model."""
                            )
                        )

                    item["dashboard_pro_dashboard_id"] = dashboard_id.id
                    item_ids.append(item["id"])
                    del item["id"]

                    if "data_calculation_type" in item:
                        if item["data_calculation_type"] == "custom":
                            del item["data_calculation_type"]
                            del item["custom_query"]
                            del item["xlabels"]
                            del item["ylabels"]
                            del item["list_view_layout"]
                            item = self.create_element(item)
                            item_new_ids.append(item.id)
                        else:
                            skiped += 1
                    else:
                        item = self.create_element(item)
                        item_new_ids.append(item.id)

            for id_index, id in enumerate(item_ids):  # pylint:disable=redefined-builtin
                if data["grid_configuration"] and str(id) in grid_configuration:
                    if id_index in item_new_ids:
                        grid_stack_config[
                            str(item_new_ids[id_index])
                        ] = grid_configuration[str(id)]

            self.browse(dashboard_id.id).write(
                {"grid_configuration": json.dumps(grid_stack_config)}
            )

            if skiped:
                return {
                    "skiped_items": skiped,
                }

        return "Success"

    def create_element(self, item):
        model = self.env["ir.model"].search([("model", "=", item["model_id"])])
        if (
            not model
            and item["type_of_element"] != "add_text"
            and item["type_of_element"] != "add_image"
            and item["type_of_element"] != "to_do"
            and item["type_of_element"] != "add_link"
        ):
            raise ValidationError(
                _("Following Model Is Not Installed : %s " % item["model_id"])
            )

        model_name = item["model_id"]

        goal_lines = (
            item["new_goal_lines"].copy()
            if item.get("new_goal_lines", False)
            else False
        )
        action_lines = (
            item["new_action_lines"].copy()
            if item.get("new_action_lines", False)
            else False
        )
        to_do_lines = (
            item["to_do_list_line"].copy()
            if item.get("to_do_list_line", False)
            else False
        )

        item = self.element_ready(item)

        if "new_goal_lines" in item:
            del item["new_goal_lines"]
        if "id" in item:
            del item["id"]
        if "new_action_lines" in item:
            del item["new_action_lines"]
        if "to_do_list_line" in item:
            del item["to_do_list_line"]

        item = self.env["dashboard_pro.element"].create(item)

        if goal_lines and len(goal_lines) != 0:
            for line in goal_lines:
                line["goal_date"] = datetime.datetime.strptime(
                    line["goal_date"].split(" ")[0], "%Y-%m-%d"
                )
                line["dashboard_element"] = item.id
                self.env["dashboard_pro.element_target"].create(line)

        if to_do_lines and len(to_do_lines) != 0:
            for line in to_do_lines:
                line["dashboard_to_do_id"] = item.id
                self.env["to_do.list"].create(line)

        if action_lines and len(action_lines) != 0:

            for line in action_lines:
                if line["sorting_selection_by_field"]:
                    sorting_selection_by_field = line["sorting_selection_by_field"]
                    sort_record_id = self.env["ir.model.fields"].search(
                        [
                            ("model", "=", model_name),
                            ("name", "=", sorting_selection_by_field),
                        ]
                    )
                    if sort_record_id:
                        line["sorting_selection_by_field"] = sort_record_id.id
                    else:
                        line["sorting_selection_by_field"] = False
                if line["item_action_field"]:
                    item_action_field = line["item_action_field"]
                    record_id = self.env["ir.model.fields"].search(
                        [("model", "=", model_name), ("name", "=", item_action_field)]
                    )
                    if record_id:
                        line["item_action_field"] = record_id.id
                        line["dashboard_item_id"] = item.id
                        self.env["dashboard_pro.element_action"].create(line)

        return item

    def element_ready(self, item):
        measure_field_ids = []
        measure_field_2_ids = []

        for measure in item["chart_data_calculation_field"]:
            measure_id = self.env["ir.model.fields"].search(
                [("name", "=", measure), ("model", "=", item["model_id"])]
            )
            if measure_id:
                measure_field_ids.append(measure_id.id)
        item["chart_data_calculation_field"] = [(6, 0, measure_field_ids)]

        for measure in item["chart_data_calculation_field_2"]:
            measure_id = self.env["ir.model.fields"].search(
                [("name", "=", measure), ("model", "=", item["model_id"])]
            )
            if measure_id:
                measure_field_2_ids.append(measure_id.id)
        item["chart_data_calculation_field_2"] = [(6, 0, measure_field_2_ids)]

        list_data_grouping = []
        for measure in item["list_data_grouping"]:
            measure_id = self.env["ir.model.fields"].search(
                [("name", "=", measure), ("model", "=", item["model_id"])]
            )

            if measure_id:
                list_data_grouping.append(measure_id.id)
        item["list_data_grouping"] = [(6, 0, list_data_grouping)]

        to_do_list_line = []
        for measure in item["to_do_list_line"]:
            measure_id = self.env["to_do.list"].create(
                {
                    "name": measure["name"],
                    "sequence": measure["sequence"],
                    "to_do_state": measure["to_do_state"],
                }
            )

            if measure_id:
                to_do_list_line.append(measure_id.id)
        item["to_do_list_line"] = [(6, 0, to_do_list_line)]

        list_view_field_ids = []
        for list_field in item["list_fields_data"]:
            list_field_id = self.env["ir.model.fields"].search(
                [("name", "=", list_field), ("model", "=", item["model_id"])]
            )
            if list_field_id:
                list_view_field_ids.append(list_field_id.id)
        item["list_fields_data"] = [(6, 0, list_view_field_ids)]

        if item["store_field_data"]:
            store_field_data = item["store_field_data"]
            record_id = self.env["ir.model.fields"].search(
                [("name", "=", store_field_data), ("model", "=", item["model_id"])]
            )
            if record_id:
                item["store_field_data"] = record_id.id
            else:
                item["store_field_data"] = False

        if item["date_filter_field"]:
            date_filter_field = item["date_filter_field"]
            record_id = self.env["ir.model.fields"].search(
                [("name", "=", date_filter_field), ("model", "=", item["model_id"])]
            )
            if record_id:
                item["date_filter_field"] = record_id.id
            else:
                item["date_filter_field"] = False

        if item["group_chart_relation"]:
            group_by = item["group_chart_relation"]
            record_id = self.env["ir.model.fields"].search(
                [("name", "=", group_by), ("model", "=", item["model_id"])]
            )
            if record_id:
                item["group_chart_relation"] = record_id.id
            else:
                item["group_chart_relation"] = False

        if item["chart_sub_field"]:
            group_by = item["chart_sub_field"]
            chart_sub_field = self.env["ir.model.fields"].search(
                [("name", "=", group_by), ("model", "=", item["model_id"])]
            )
            if chart_sub_field:
                item["chart_sub_field"] = chart_sub_field.id
            else:
                item["chart_sub_field"] = False

        if item["sorting_selection_by_field"]:
            group_by = item["sorting_selection_by_field"]
            sorting_selection_by_field = self.env["ir.model.fields"].search(
                [("name", "=", group_by), ("model", "=", item["model_id"])]
            )
            if sorting_selection_by_field:
                item["sorting_selection_by_field"] = sorting_selection_by_field.id
            else:
                item["sorting_selection_by_field"] = False

        if item["list_goal_field"]:
            list_goal_field = item["list_goal_field"]
            record_id = self.env["ir.model.fields"].search(
                [("name", "=", list_goal_field), ("model", "=", item["model_id"])]
            )
            if record_id:
                item["list_goal_field"] = record_id.id
            else:
                item["list_goal_field"] = False

        model_id = self.env["ir.model"].search([("model", "=", item["model_id"])]).id

        if item["actions"]:
            action = self.env.ref(item["actions"], False)
            if action:
                item["actions"] = action.id
            else:
                item["actions"] = False

        if item["ir_model_field_2"]:
            ir_model_field_2 = (
                self.env["ir.model"]
                .search([("model", "=", item["ir_model_field_2"])])
                .id
            )
            if item["store_field_data_2"]:
                store_field_data = item["store_field_data_2"]
                record_id = self.env["ir.model.fields"].search(
                    [
                        ("model", "=", item["ir_model_field_2"]),
                        ("name", "=", store_field_data),
                    ]
                )

                if record_id:
                    item["store_field_data_2"] = record_id.id
                else:
                    item["store_field_data_2"] = False
            if item["date_filter_field_2"]:
                record_id = self.env["ir.model.fields"].search(
                    [
                        ("model", "=", item["ir_model_field_2"]),
                        ("name", "=", item["date_filter_field_2"]),
                    ]
                )

                if record_id:
                    item["date_filter_field_2"] = record_id.id
                else:
                    item["date_filter_field_2"] = False

            item["ir_model_field_2"] = ir_model_field_2
        else:
            item["date_filter_field_2"] = False
            item["store_field_data_2"] = False

        item["model_id"] = model_id

        item["new_goal_lines"] = False
        item["element_start_date"] = (
            datetime.datetime.strptime(
                item["element_start_date"].split(" ")[0], "%Y-%m-%d"
            )
            if item["element_start_date"]
            else False
        )
        item["element_end_date"] = (
            datetime.datetime.strptime(
                item["element_end_date"].split(" ")[0], "%Y-%m-%d"
            )
            if item["element_end_date"]
            else False
        )
        item["starting_date_kpi_2"] = (
            datetime.datetime.strptime(
                item["starting_date_kpi_2"].split(" ")[0], "%Y-%m-%d"
            )
            if item["starting_date_kpi_2"]
            else False
        )
        item["ending_date_kpi_2"] = (
            datetime.datetime.strptime(
                item["ending_date_kpi_2"].split(" ")[0], "%Y-%m-%d"
            )
            if item["ending_date_kpi_2"]
            else False
        )

        return item


class DashboardProTemplate(models.Model):
    _name = "dashboard_pro.dashboard_template"
    _description = "Dashboard Template"

    name = fields.Char()
    grid_configuration = fields.Char()
    item_count = fields.Integer()


class DashboardProBoardItemAction(models.TransientModel):
    _name = "pro_dashboard_pro.item_action"
    _description = "Dashboard Item Action"

    name = fields.Char()
    dashboard_item_ids = fields.Many2many(
        "dashboard_pro.element", string="Dashboard Items"
    )
    action = fields.Selection(
        [
            ("move", "Move"),
            ("duplicate", "Duplicate"),
        ],
        string="Action",
    )
    dashboard_pro_id = fields.Many2one(
        "dashboard_pro.main_dashboard", string="Select Dashboard"
    )
    dashboard_pro_ids = fields.Many2many(
        "dashboard_pro.main_dashboard", string="Select Dashboards"
    )

    def action_item_move_copy_action(self):

        if self.action == "move":
            for item in self.dashboard_item_ids:
                item.dashboard_pro_dashboard_id = self.dashboard_pro_id

        elif self.action == "duplicate":
            for dashboard_id in self.dashboard_pro_ids:
                for item in self.dashboard_item_ids:
                    item.sudo().copy({"dashboard_pro_dashboard_id": dashboard_id.id})
