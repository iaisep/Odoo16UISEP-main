# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json
from datetime import datetime

import babel
import pytz
from dateutil import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import safe_eval

from ..lib.filter_function import generate_date


class DashboardToDoList(models.Model):
    _name = "to_do.list"
    _description = "Model For To Do List"
    _order = "sequence asc"

    name = fields.Char(string="Name:")
    sequence = fields.Integer(string="Sequence", required=True, default=10)
    to_do_state = fields.Selection(
        [("to_do", "To Do"), ("done", "Done"), ("delete", "Deleted")], default="to_do"
    )
    dashboard_to_do_id = fields.Many2one("dashboard_pro.element")

    def to_do_list_delete_func(self):
        self.to_do_state = "delete"
        return self.name

    def to_do_list_state_change_func(self, state):
        if state == "to_do":
            self.to_do_state = "done"
        if state == "done":
            self.to_do_state = "to_do"

        return True


class DashboardProElement(models.Model):
    _name = "dashboard_pro.element"
    _description = "Dashboard Element Model And object"

    name = fields.Char(string="Name:")
    model_id = fields.Many2one("ir.model", string="Model ")
    domain = fields.Char(string="Domain")

    ir_model_field_2 = fields.Many2one("ir.model", string="Model")

    ir_model_field_2_name = fields.Char(
        related="ir_model_field_2.model", string="Model Name"
    )

    background_color = fields.Char(string="Background Color", default="#ffffff,0.99")
    icon = fields.Binary(string="Upload Icon", attachment=True)
    default_icon = fields.Char(string="Icon", default="bar-chart")
    default_icon_color = fields.Char(default="#000000,0.99", string="Icon Color")
    selection_icon_field = fields.Char(string="Icon Option", default="Default")
    font_color = fields.Char(default="#000000,0.99", string="Font Color")
    element_theme = fields.Char(string="Theme", default="blue")
    layout = fields.Selection(
        [
            ("layout1", "Layout 1"),
            ("layout2", "Layout 2"),
            ("layout3", "Layout 3"),
            ("layout4", "Layout 4"),
            ("layout5", "Layout 5"),
            ("layout6", "Layout 6"),
            ("state_layout_1", "State Layout 1"),
            ("state_layout_2", "State Layout 2"),
        ],
        default=("layout1"),
        required=True,
        string="Layout",
    )
    state_layout_state = fields.Selection(
        [
            ("approved", "Approved"),
            ("pending", "Pending"),
            ("rejected", "Rejected"),
            ("custom", "Custom"),
        ],
        string="State ",
    )
    state_layout_state_1 = fields.Selection(
        [
            ("approved", "Approved"),
            ("pending", "Pending"),
            ("rejected", "Rejected"),
            ("custom", "Custom"),
        ],
        string="State",
    )
    preview = fields.Integer(default=1, string="Preview")
    model_name = fields.Char(related="model_id.model", string="Model Name ")
    data_calculation_value = fields.Float(
        string="Record Count",
        compute="_compute_get_data_calculation",
        readonly=True,
        compute_sudo=False,
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.user.company_id
    )

    type_of_element = fields.Selection(
        [
            ("tile", "Tile"),
            ("add_text", "Text"),
            ("add_link", "Link"),
            ("bar_chart", "Bar Chart"),
            ("horizontalBar_chart", "Horizontal Bar Chart"),
            ("line_chart", "Line Chart"),
            ("area_chart", "Area Chart"),
            ("pie_chart", "Pie Chart"),
            ("doughnut_chart", "Doughnut Chart"),
            ("polarArea_chart", "Polar Area Chart"),
            ("list_view", "List View"),
            ("add_divider", "Divider"),
            ("add_image", "Image"),
            ("kpi", "KPI"),
            ("to_do", "To-Do List"),
        ],
        default=lambda self: self._context.get("type_of_element", "tile"),
        required=True,
        string="Dashboard Item Type",
    )
    update_element_data_time = fields.Selection(
        [
            ("15000", "15 Seconds"),
            ("30000", "30 Seconds"),
            ("45000", "45 Seconds"),
            ("60000", "1 minute"),
            ("120000", "2 minute"),
            ("300000", "5 minute"),
            ("600000", "10 minute"),
        ],
        string="Item Update Interval",
        default=lambda self: self._context.get("interval_time", False),
    )
    graph_preview = fields.Char(string="Graph Preview", default="Graph Preview")
    store_field_data = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',model_id),('name','!=','id'),('store','=',True),'|',"
        "'|',('ttype','=','integer'),('ttype','=','float'),"
        "('ttype','=','monetary')]",
        string="Record Field",
    )
    data_calculation_type_chart = fields.Selection(
        [("count", "Count"), ("sum", "Sum"), ("average", "Average")],
        string="Data Type",
        default="sum",
    )
    chart_data_calculation_field = fields.Many2many(
        "ir.model.fields",
        "dn_measure_field_rel",
        "measure_field_id",
        "field_id",
        domain="[('model_id','=',model_id),('name','!=','id'),"
        "('store','=',True),'|','|',"
        "('ttype','=','integer'),('ttype','=','float'),"
        "('ttype','=','monetary')]",
        string="Measure 1",
    )

    chart_data_calculation_field_2 = fields.Many2many(
        "ir.model.fields",
        "dn_measure_field_rel_2",
        "measure_field_id_2",
        "field_id",
        domain="[('model_id','=',model_id),('name','!=','id'),"
        "('store','=',True),'|','|',"
        "('ttype','=','integer'),('ttype','=','float'),"
        "('ttype','=','monetary')]",
        string="Line Measure",
    )
    list_view_type = fields.Selection(
        [("ungrouped", "Un-Grouped"), ("grouped", "Grouped")],
        default="ungrouped",
        string="List View Type",
        required=True,
    )
    list_preview = fields.Char(string="List View Preview", default="List View Preview")

    list_fields_data = fields.Many2many(
        "ir.model.fields",
        "dn_list_field_rel",
        "list_field_id",
        "field_id",
        domain="[('model_id','=',model_id),('ttype','!=','one2many'),"
        "('ttype','!=','many2many'),('ttype','!=','binary')]",
        string="Fields to show in list",
    )

    list_data_grouping = fields.Many2many(
        "ir.model.fields",
        "dn_list_group_field_rel",
        "list_field_id",
        "field_id",
        domain="[('model_id','=',model_id),('name','!=','id'),"
        "('store','=',True),'|','|',"
        "('ttype','=','integer'),('ttype','=','float'),"
        "('ttype','=','monetary')]",
        string="List View Grouped Fields",
    )

    json_list_data = fields.Char(
        string="List View Data in JSon",
        compute="_compute_list_element_info_func",
        compute_sudo=False,
    )

    to_do_list_line = fields.One2many(
        "to_do.list", "dashboard_to_do_id", string="To Do List"
    )
    to_do_list_preview = fields.Char(
        string="To-Do List Preview", default="To-Do List View Preview"
    )
    to_do_list_count = fields.Char(
        string="Total Of To Do List", compute="_compute_to_do_list_total_count"
    )
    json_todo_list_data = fields.Char(
        string="To-Do Data In Json", compute="_compute_todo_list_element_info_func"
    )

    list_goal_field = fields.Many2one(
        "ir.model.fields",
        "list_field_id",
        domain="[('model_id','=',model_id),('name','!=','id'),"
        "('store','=',True),'|','|',"
        "('ttype','=','integer'),('ttype','=','float'),"
        "('ttype','=','monetary')]",
    )
    group_chart_field = fields.Char(
        string="Chart GroupBy", compute="_compute_chart_group_type_fun",
        compute_sudo=False
    )
    sub_group_chart_field = fields.Char(
        compute="_compute_chart_group_type_func", compute_sudo=False
    )
    group_chart_relation = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',model_id),('name','!=','id'),"
        "('store','=',True),('ttype','!=','binary'),"
        "('ttype','!=','many2many'), ('ttype','!=','one2many')]",
        string="Group By",
    )
    is_goal_enable = fields.Boolean(string="Enable Target")
    goal_line_field = fields.Boolean(string="Show Target As Line")
    goal_value_field = fields.Float(string="Standard Target")
    goal_lines = fields.One2many(
        "dashboard_pro.element_target", "dashboard_element", string="Target Lines"
    )
    target_view = fields.Char(string="View", default="Number")
    chart_sub_field = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',model_id),('name','!=','id'),"
        "('store','=',True),('ttype','!=','binary'),"
        "('ttype','!=','many2many'), ('ttype','!=','one2many')]",
        string=" Sub Group By",
    )
    kpi_compare_field = fields.Char(string="Kpi Data Type", default="None")
    chart_group_field = fields.Selection(
        [
            ("minute", "Minute"),
            ("hour", "Hour"),
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        string="Dashboard Item Chart Group By Type",
    )
    chart_sub_field_date = fields.Selection(
        [
            ("minute", "Minute"),
            ("hour", "Hour"),
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        string="Dashboard Item Chart Sub Group By Type",
    )
    sorting_selection_by_field = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',model_id),('name','!=','id'),('store','=',True),"
        "('ttype','!=','one2many'),('ttype','!=','binary')]",
        string="Sort By Field",
    )
    sorting_selection = fields.Selection(
        [("ASC", "Ascending"), ("DESC", "Descending")], string="Sort Order"
    )
    filter_limit = fields.Integer(string="Record Limit")

    date_filter_field = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',model_id),'|',('ttype','=','date'),"
        "('ttype','=','datetime')]",
        string="Date Filter Field",
    )
    element_start_date = fields.Datetime(string="Start Date")
    element_end_date = fields.Datetime(string="End Date")
    time_of_comparation = fields.Integer(string="Include Period ")
    year_period = fields.Integer(string="Same Period Previous Years ")
    date_domain_fields = fields.Selection(
        [
            ("none", "None"),
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
        string="Date Filter Selection",
        default="none",
        required=True,
    )

    kpi_preview = fields.Char(string="Kpi Preview", default="KPI Preview")
    record_count_2 = fields.Float(
        string="KPI Record Count",
        readonly=True,
        compute="_compute_data_calculation_func_1",
        compute_sudo=False,
    )
    kpi_data = fields.Char(
        string="KPI Data", compute="_compute_kpi_info_func", compute_sudo=False
    )
    previous_data_field = fields.Boolean(string="Previous Period")
    chart_theme_selection = fields.Selection(
        [("default", "Default"), ("cool", "Cool"), ("warm", "Warm"), ("neon", "Neon")],
        string="Chart Chart Theme",
        default="default",
    )
    time_of_comparation_2 = fields.Integer(string="Include Period")
    year_period_2 = fields.Integer(string="Same Period Previous Years")
    domain_2 = fields.Char(string="Kpi Domain")

    date_filter_selection_2 = fields.Selection(
        [
            ("none", "None"),
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
        string="Kpi Date Filter Selection",
        required=True,
        default="none",
    )
    store_field_data_2 = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',ir_model_field_2),"
        "('name','!=','id'),('store','=',True),"
        "'|','|',('ttype','=','integer'),('ttype','=','float'),"
        "('ttype','=','monetary')]",
        string="Kpi Record Field",
    )
    data_calculation_type = fields.Selection(
        [("count", "Count"), ("sum", "Sum"), ("average", "Average")],
        string="Record Type",
        default="sum",
    )
    starting_date_kpi_2 = fields.Datetime(string="Kpi Start Date")
    ending_date_kpi_2 = fields.Datetime(string="Kpi End Date")

    date_filter_field_2 = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',ir_model_field_2),'|',('ttype','=','date'),"
        "('ttype','=','datetime')]",
        string="Kpi Date Filter Field",
    )
    chart_data = fields.Char(
        string="Chart Data in string form",
        compute="_compute_chart_data_func",
        compute_sudo=False,
    )
    unit = fields.Boolean(string="Show Custom Unit", default=False)
    unit_selection = fields.Selection(
        [
            ("monetary", "Monetary"),
            ("custom", "Custom"),
        ],
        string="Select Unit Type",
    )
    chart_unit = fields.Char(
        string="Enter Unit",
        size=5,
        default="",
        help="Maximum limit 5 characters, for ex: km, m",
    )

    dashboard_pro_dashboard_id = fields.Many2one(
        "dashboard_pro.main_dashboard",
        string="Dashboard",
        default=lambda self: self._context["dashboard_id"]
        if "dashboard_id" in self._context
        else False,
    )
    actions = fields.Many2one(
        "ir.actions.act_window",
        domain="[('res_model','=',model_name)]",
        string="Actions",
        help="This Action will be Performed at the end of Drill Down Action",
    )
    bar_chart_stacked = fields.Boolean(string="Stacked Bar Chart")
    show_data_value = fields.Boolean(string="Show Data Value")
    semi_circle_chart = fields.Boolean(string="Semi Circle Chart")
    show_records = fields.Boolean(string="Show Records", default=True)
    many2many_field_ordering = fields.Char()
    action_lines = fields.One2many(
        "dashboard_pro.element_action", "dashboard_item_id", string="Action Lines"
    )
    add_text_preview = fields.Integer("Text Preview")
    add_text_main_content = fields.Text("Text Content", default="Add Something Here")
    add_text_custom_bold = fields.Boolean("Bold Text")
    add_text_align = fields.Selection(
        [("left", "Left"), ("center", "Center"), ("right", "Right")]
    )
    add_text_custom_italic = fields.Boolean("Italic Text")
    add_text_custom_font_size = fields.Integer("Font Size ", default="20")
    add_text_font_style = fields.Selection(
        [
            ("h1", "Header 1"),
            ("h2", "Header 2"),
            ("h3", "Header 3"),
            ("p", "Paragraph"),
            ("custom", "Custom"),
        ],
        default="h3",
    )

    add_link_content = fields.Char("Link", default="www.google.com")
    add_link_preview = fields.Integer("Link Preview")
    add_link_title = fields.Boolean("Add Name As Title?")

    add_image_image = fields.Binary("Image", attachment=True)

    add_divider_line = fields.Selection(
        [("horizontal", "Horizontal"), ("vertical", "Vertical")]
    )

    @api.onchange("state_layout_state")
    def onchange_state_layout_state(self):
        self.name = dict(self._fields["state_layout_state"].selection).get(
            self.state_layout_state
        )
        if self.state_layout_state == "approved":
            self.default_icon = "check-circle-o"
            self.background_color = "#5f9823,0.99"
        if self.state_layout_state == "rejected":
            self.default_icon = "times-circle-o"
            self.background_color = "#882525,0.99"
        if self.state_layout_state == "pending":
            self.default_icon = "clock-o"
            self.background_color = "#e3c034,0.99"
        if self.state_layout_state == "custom":
            self.default_icon = "question-circle-o"
            self.background_color = "#3279b6,0.99"

    @api.onchange("state_layout_state_1")
    def onchange_state_layout_state_1(self):
        self.name = dict(self._fields["state_layout_state_1"].selection).get(
            self.state_layout_state_1
        )
        self.default_icon_color = "#000000,0.99"
        self.font_color = "#000000,0.99"
        if self.state_layout_state_1 == "approved":
            self.default_icon = "check-circle-o"
            self.background_color = "#5f9823,0.99"
        if self.state_layout_state_1 == "rejected":
            self.default_icon = "times-circle-o"
            self.background_color = "#882525,0.99"
        if self.state_layout_state_1 == "pending":
            self.default_icon = "clock-o"
            self.background_color = "#d9d243,0.99"
        if self.state_layout_state_1 == "custom":
            self.default_icon = "question"
            self.background_color = "#3279b6,0.99"

    @api.model_create_multi
    def create(self, values):
        """ Override to save list view fields ordering """
        if len(self) > 0:
            for rec in values:
                if rec.get("type_of_element") == "to_do":
                    to_do_list_line = []
                    for measure in self.to_do_list_line:
                        measure_id = self.env["to_do.list"].create(
                            {
                                "name": measure["name"],
                                "sequence": measure["sequence"],
                                "to_do_state": measure["to_do_state"],
                            }
                        )

                        if measure_id:
                            to_do_list_line.append(measure_id.id)
                    rec["to_do_list_line"] = [(6, 0, to_do_list_line)]
            if rec.get("list_fields_data", False) and rec.get(
                "list_data_grouping", False
            ):
                many2many_field_ordering = {
                    "list_fields_data": rec["list_fields_data"][0][2],
                    "list_data_grouping": rec["list_data_grouping"][0][2],
                }
                rec["many2many_field_ordering"] = json.dumps(many2many_field_ordering)

        return super(DashboardProElement, self).create(values)

    def write(self, values):
        for dashboard_rec in self:
            if dashboard_rec["many2many_field_ordering"]:
                many2many_field_ordering = json.loads(
                    dashboard_rec["many2many_field_ordering"]
                )
            else:
                many2many_field_ordering = {}
            if values.get("list_fields_data", False):
                many2many_field_ordering["list_fields_data"] = values[
                    "list_fields_data"
                ][0][2]
            if values.get("list_data_grouping", False):
                many2many_field_ordering["list_data_grouping"] = values[
                    "list_data_grouping"
                ][0][2]
            if values.get("to_do_list_line", False):
                many2many_field_ordering["to_do_list_line"] = values["to_do_list_line"][
                    0
                ][2]
            values["many2many_field_ordering"] = json.dumps(many2many_field_ordering)

        return super(DashboardProElement, self).write(values)

    @api.onchange(
        "layout",
        "name",
        "model_id",
        "domain",
        "selection_icon_field",
        "default_icon",
        "icon",
        "background_color",
        "data_calculation_type",
        "data_calculation_value",
        "font_color",
        "default_icon_color",
    )
    def update_form_view(self):
        self.preview += 1

    @api.onchange(
        "add_text_font_style",
        "add_text_custom_font_size",
        "add_text_custom_bold",
        "add_text_align",
        "add_text_custom_italic",
        "add_text_main_content",
        "background_color",
        "font_color",
    )
    def update_add_text_view(self):
        self.add_text_preview += 1

    @api.onchange("add_link_content", "add_link_title", "name")
    def update_add_link_preview(self):
        if self.add_link_title is True and self.name is False:
            self.name = "Title"
        self.add_link_preview += 1

    @api.depends(
        "data_calculation_type",
        "model_id",
        "domain",
        "store_field_data",
        "date_filter_field",
        "element_end_date",
        "element_start_date",
        "time_of_comparation",
        "year_period",
        "type_of_element",
    )
    def _compute_get_data_calculation(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.data_calculation_type == "count"
                or dashboard_rec.type_of_element == "list_view"
            ):
                dashboard_rec.data_calculation_value = (
                    dashboard_rec.getting_data_of_model(
                        dashboard_rec.model_name,
                        dashboard_rec.domain,
                        "search_count",
                        dashboard_rec,
                    )
                )
            elif (
                dashboard_rec.data_calculation_type in ["sum", "average"]
                and dashboard_rec.store_field_data
                and dashboard_rec.type_of_element != "list_view"
            ):
                records_grouped_data = dashboard_rec.getting_data_of_model(
                    dashboard_rec.model_name,
                    dashboard_rec.domain,
                    "read_group",
                    dashboard_rec,
                )
                if records_grouped_data and len(records_grouped_data) > 0:
                    records_grouped_data = records_grouped_data[0]
                    if (
                        dashboard_rec.data_calculation_type == "sum"
                        and records_grouped_data.get("__count", False)
                        and (
                            records_grouped_data.get(
                                dashboard_rec.store_field_data.name
                            )
                        )
                    ):
                        dashboard_rec.data_calculation_value = records_grouped_data.get(
                            dashboard_rec.store_field_data.name, 0
                        )
                    elif (
                        dashboard_rec.data_calculation_type == "average"
                        and records_grouped_data.get("__count", False)
                        and (
                            records_grouped_data.get(
                                dashboard_rec.store_field_data.name
                            )
                        )
                    ):
                        dashboard_rec.data_calculation_value = records_grouped_data.get(
                            dashboard_rec.store_field_data.name, 0
                        ) / records_grouped_data.get("__count", 1)
                    else:
                        dashboard_rec.data_calculation_value = 0
                else:
                    dashboard_rec.data_calculation_value = 0
            else:
                dashboard_rec.data_calculation_value = 0

    def getting_data_of_model(self, model_name, domain, func, dashboard_rec):
        data = 0
        try:
            if domain and domain != "[]" and model_name:
                proper_domain = self.convert_into_proper_domain(domain, dashboard_rec)
                if func == "search_count":
                    data = self.env[model_name].search_count(proper_domain)
                elif func == "read_group":
                    data = self.env[model_name].read_group(
                        proper_domain, [dashboard_rec.store_field_data.name], []
                    )
            elif model_name:
                proper_domain = self.convert_into_proper_domain(False, dashboard_rec)
                if func == "search_count":
                    data = self.env[model_name].search_count(proper_domain)

                elif func == "read_group":
                    data = self.env[model_name].read_group(
                        proper_domain, [dashboard_rec.store_field_data.name], []
                    )
            else:
                return []
        except Exception:
            return []
        return data

    @api.depends("group_chart_relation")
    def _compute_chart_group_type_fun(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.group_chart_relation.ttype == "datetime"
                or dashboard_rec.group_chart_relation.ttype == "date"
            ):
                dashboard_rec.group_chart_field = "date_type"
            elif dashboard_rec.group_chart_relation.ttype == "many2one":
                dashboard_rec.group_chart_field = "relational_type"
            elif dashboard_rec.group_chart_relation.ttype == "selection":
                dashboard_rec.group_chart_field = "selection"
            else:
                dashboard_rec.group_chart_field = "other"

    @api.onchange("group_chart_relation")
    def empty_sub_group_by(self):
        for dashboard_rec in self:
            if (
                not dashboard_rec.group_chart_relation
                or dashboard_rec.group_chart_field == "date_type"
                and not dashboard_rec.chart_group_field
            ):
                dashboard_rec.chart_sub_field = False
                dashboard_rec.chart_sub_field_date = False

    @api.depends("to_do_list_line")
    def _compute_to_do_list_total_count(self):
        self.to_do_list_count = len(self.to_do_list_line)

    @api.depends("type_of_element", "to_do_list_line")
    def _compute_todo_list_element_info_func(self):
        for dashboard_rec in self:
            if dashboard_rec.type_of_element == "to_do":
                json_todo_list_data = {
                    "data_rows": [],
                    "model": "to_do.list",
                    "label": ["Done", "To-Do List", ""],
                }
                for i in dashboard_rec.to_do_list_line:
                    data_row = {"data": [], "state": ""}
                    if i.to_do_state == "to_do" or i.to_do_state == "done":
                        data_row["state"] = i.to_do_state
                        data_row["data"].append(i.name)

                    json_todo_list_data["data_rows"].append(data_row)

                dashboard_rec.json_todo_list_data = json.dumps(json_todo_list_data)
            else:
                dashboard_rec.json_todo_list_data = False

    @api.depends(
        "domain",
        "type_of_element",
        "model_id",
        "sorting_selection_by_field",
        "sorting_selection",
        "filter_limit",
        "list_fields_data",
        "list_view_type",
        "list_data_grouping",
        "group_chart_field",
        "chart_group_field",
        "date_filter_field",
        "element_end_date",
        "element_start_date",
        "time_of_comparation",
        "year_period",
        "list_goal_field",
        "is_goal_enable",
        "goal_value_field",
        "goal_lines",
    )
    def _compute_list_element_info_func(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.list_view_type
                and dashboard_rec.type_of_element
                and dashboard_rec.type_of_element == "list_view"
                and dashboard_rec.model_id
            ):
                json_list_data = {
                    "label": [],
                    "type": dashboard_rec.list_view_type,
                    "data_rows": [],
                    "model": dashboard_rec.model_name,
                }

                chart_domain = self.convert_into_proper_domain(
                    dashboard_rec.domain, dashboard_rec
                )
                orderby = (
                    dashboard_rec.sorting_selection_by_field.name
                    if dashboard_rec.sorting_selection_by_field
                    else "id"
                )
                if dashboard_rec.sorting_selection:
                    orderby = orderby + " " + dashboard_rec.sorting_selection
                limit = (
                    dashboard_rec.filter_limit
                    if dashboard_rec.filter_limit and dashboard_rec.filter_limit > 0
                    else False
                )

                if dashboard_rec.list_view_type == "ungrouped":
                    if dashboard_rec.list_fields_data:
                        json_list_data = dashboard_rec.list_info_sub_func(dashboard_rec)

                elif (
                    dashboard_rec.list_view_type == "grouped"
                    and dashboard_rec.list_data_grouping
                    and dashboard_rec.group_chart_relation
                ):
                    list_fields = []

                    if dashboard_rec.group_chart_field == "relational_type":
                        json_list_data["list_view_type"] = "relational_type"
                        json_list_data[
                            "groupby"
                        ] = dashboard_rec.group_chart_relation.name
                        list_fields.append(dashboard_rec.group_chart_relation.name)
                        json_list_data["label"].append(
                            dashboard_rec.group_chart_relation.field_description
                        )
                        for res in dashboard_rec.list_data_grouping:
                            list_fields.append(res.name)
                            json_list_data["label"].append(res.field_description)

                        list_view_records = self.env[
                            dashboard_rec.model_name
                        ].read_group(
                            chart_domain,
                            list_fields,
                            [dashboard_rec.group_chart_relation.name],
                            orderby=orderby,
                            limit=limit,
                        )
                        for res in list_view_records:
                            if (
                                all(list_fields in res for list_fields in list_fields)
                                and res[dashboard_rec.group_chart_relation.name]
                            ):
                                counter = 0
                                data_row = {
                                    "id": res[dashboard_rec.group_chart_relation.name][
                                        0
                                    ],
                                    "data": [],
                                    "domain": json.dumps(res["__domain"]),
                                }
                                for field_rec in list_fields:
                                    if counter == 0:
                                        data_row["data"].append(res[field_rec][1])
                                    else:
                                        data_row["data"].append(res[field_rec])
                                    counter += 1
                                json_list_data["data_rows"].append(data_row)

                    elif (
                        dashboard_rec.group_chart_field == "date_type"
                        and dashboard_rec.chart_group_field
                    ):
                        json_list_data["list_view_type"] = "date_type"
                        list_field = []
                        json_list_data["groupby"] = (
                            dashboard_rec.group_chart_relation.name
                            + ":"
                            + dashboard_rec.chart_group_field
                        )
                        list_field.append(dashboard_rec.group_chart_relation.name)
                        list_fields.append(
                            dashboard_rec.group_chart_relation.name
                            + ":"
                            + dashboard_rec.chart_group_field
                        )
                        json_list_data["label"].append(
                            dashboard_rec.group_chart_relation.field_description
                            + " : "
                            + dashboard_rec.chart_group_field.capitalize()
                        )
                        for res in dashboard_rec.list_data_grouping:
                            list_fields.append(res.name)
                            list_field.append(res.name)
                            json_list_data["label"].append(res.field_description)

                        list_goal_field = []
                        if (
                            dashboard_rec.is_goal_enable
                            and dashboard_rec.list_goal_field
                        ):
                            list_goal_field.append(dashboard_rec.list_goal_field.name)
                            if dashboard_rec.list_goal_field.name in list_field:
                                list_field.remove(dashboard_rec.list_goal_field.name)
                                list_fields.remove(dashboard_rec.list_goal_field.name)
                                json_list_data["label"].remove(
                                    dashboard_rec.list_goal_field.field_description
                                )

                        list_view_records = self.env[
                            dashboard_rec.model_name
                        ].read_group(
                            chart_domain,
                            list_field + list_goal_field,
                            [
                                dashboard_rec.group_chart_relation.name
                                + ":"
                                + dashboard_rec.chart_group_field
                            ],
                            orderby=orderby,
                            limit=limit,
                        )
                        if all(
                            list_fields in res
                            for res in list_view_records
                            for list_fields in list_fields + list_goal_field
                        ):
                            for res in list_view_records:
                                counter = 0
                                data_row = {
                                    "id": 0,
                                    "data": [],
                                    "domain": json.dumps(res["__domain"]),
                                }
                                for field_rec in list_fields:
                                    data_row["data"].append(res[field_rec])
                                json_list_data["data_rows"].append(data_row)

                            if dashboard_rec.is_goal_enable:
                                list_labels = []
                                json_list_data["label"].append("Target")

                                if dashboard_rec.list_goal_field:
                                    json_list_data["label"].append(
                                        dashboard_rec.list_goal_field.field_description
                                    )
                                    json_list_data["label"].append("Achievement")
                                    json_list_data["label"].append("Deviation")

                                for res in list_view_records:
                                    list_labels.append(res[json_list_data["groupby"]])
                                list_view_data2 = (
                                    dashboard_rec.get_target_list_view_data(
                                        list_view_records,
                                        dashboard_rec,
                                        list_fields,
                                        json_list_data["groupby"],
                                        list_goal_field,
                                        chart_domain,
                                    )
                                )
                                json_list_data["data_rows"] = list_view_data2[
                                    "data_rows"
                                ]

                    elif dashboard_rec.group_chart_field == "selection":
                        json_list_data["list_view_type"] = "selection"
                        json_list_data[
                            "groupby"
                        ] = dashboard_rec.group_chart_relation.name
                        selection_field = dashboard_rec.group_chart_relation.name
                        json_list_data["label"].append(
                            dashboard_rec.group_chart_relation.field_description
                        )
                        for res in dashboard_rec.list_data_grouping:
                            list_fields.append(res.name)
                            json_list_data["label"].append(res.field_description)

                        list_view_records = self.env[
                            dashboard_rec.model_name
                        ].read_group(
                            chart_domain,
                            list_fields,
                            [dashboard_rec.group_chart_relation.name],
                            orderby=orderby,
                            limit=limit,
                        )
                        for res in list_view_records:
                            if all(list_fields in res for list_fields in list_fields):
                                counter = 0
                                data_row = {
                                    "id": 0,
                                    "data": [],
                                    "domain": json.dumps(res["__domain"]),
                                }
                                if res[selection_field]:
                                    data_row["data"].append(
                                        dict(
                                            self.env[
                                                dashboard_rec.model_name
                                            ].fields_get(allfields=selection_field)[
                                                selection_field
                                            ][
                                                "selection"
                                            ]
                                        )[res[selection_field]]
                                    )
                                else:
                                    data_row["data"].append(" ")
                                for field_rec in list_fields:
                                    data_row["data"].append(res[field_rec])
                                json_list_data["data_rows"].append(data_row)

                    elif dashboard_rec.group_chart_field == "other":
                        json_list_data["list_view_type"] = "other"
                        json_list_data[
                            "groupby"
                        ] = dashboard_rec.group_chart_relation.name
                        list_fields.append(dashboard_rec.group_chart_relation.name)
                        json_list_data["label"].append(
                            dashboard_rec.group_chart_relation.field_description
                        )
                        for res in dashboard_rec.list_data_grouping:
                            list_fields.append(res.name)
                            json_list_data["label"].append(res.field_description)

                        list_view_records = self.env[
                            dashboard_rec.model_name
                        ].read_group(
                            chart_domain,
                            list_fields,
                            [dashboard_rec.group_chart_relation.name],
                            orderby=orderby,
                            limit=limit,
                        )
                        for res in list_view_records:
                            if all(list_fields in res for list_fields in list_fields):
                                counter = 0
                                data_row = {
                                    "id": 0,
                                    "data": [],
                                    "domain": json.dumps(res["__domain"]),
                                }

                                for field_rec in list_fields:
                                    if counter == 0:
                                        data_row["data"].append(res[field_rec])
                                    else:
                                        if (
                                            dashboard_rec.group_chart_relation.name
                                            == field_rec
                                        ):
                                            data_row["data"].append(
                                                res[field_rec]
                                                * res[field_rec + "_count"]
                                            )
                                        else:
                                            data_row["data"].append(res[field_rec])
                                    counter += 1
                                json_list_data["data_rows"].append(data_row)

                dashboard_rec.json_list_data = json.dumps(json_list_data)
            else:
                dashboard_rec.json_list_data = False

    @api.onchange("type_of_element")
    def set_color_palette(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.type_of_element == "bar_chart"
                or dashboard_rec.type_of_element == "horizontalBar_chart"
                or dashboard_rec.type_of_element == "line_chart"
                or dashboard_rec.type_of_element == "area_chart"
            ):
                dashboard_rec.chart_theme_selection = "cool"
            else:
                dashboard_rec.chart_theme_selection = "default"

    @api.model
    def list_info_sub_func(self, dashboard_rec, limit=15, offset=0):
        json_list_data = {
            "label": [],
            "type": "ungrouped",
            "data_rows": [],
            "model": dashboard_rec.model_name,
        }

        chart_domain = dashboard_rec.convert_into_proper_domain(
            dashboard_rec.domain, dashboard_rec
        )
        orderby = (
            dashboard_rec.sorting_selection_by_field.name
            if dashboard_rec.sorting_selection_by_field
            else "id"
        )
        if dashboard_rec.sorting_selection:
            orderby = orderby + " " + dashboard_rec.sorting_selection
        limit = (
            dashboard_rec.filter_limit
            if dashboard_rec.filter_limit and dashboard_rec.filter_limit > 0
            else False
        )

        if limit:
            limit = limit - offset
            if limit and limit < 15:
                limit = limit
            else:
                limit = 15
        if dashboard_rec.list_fields_data:
            json_list_data["list_view_type"] = "other"
            json_list_data["groupby"] = False
            json_list_data["label"] = []
            json_list_data["date_index"] = []
            for res in dashboard_rec.list_fields_data:
                if res.ttype == "datetime" or res.ttype == "date":
                    index = len(json_list_data["label"])
                    json_list_data["label"].append(res.field_description)
                    json_list_data["date_index"].append(index)
                else:
                    json_list_data["label"].append(res.field_description)

            list_fields_data = [res.name for res in dashboard_rec.list_fields_data]
            list_view_field_type = [res.ttype for res in dashboard_rec.list_fields_data]
        try:
            list_view_records = self.env[dashboard_rec.model_name].search_read(
                chart_domain,
                list_fields_data,
                order=orderby,
                limit=limit,
                offset=offset,
            )
        except Exception:
            json_list_data = False
            return json_list_data
        for res in list_view_records:
            counter = 0
            data_row = {"id": res["id"], "data": []}
            for field_rec in list_fields_data:
                if (
                    type(res[field_rec]) == fields.datetime
                    or type(res[field_rec]) == fields.date
                ):
                    res[field_rec] = res[field_rec].strftime("%D %T")
                elif list_view_field_type[counter] == "many2one":
                    if res[field_rec]:
                        res[field_rec] = res[field_rec][1]
                data_row["data"].append(res[field_rec])
                counter += 1
            json_list_data["data_rows"].append(data_row)

        return json_list_data

    def convert_into_proper_domain(self, domain, dashboard_rec):
        if domain and "%UID" in domain:
            domain = domain.replace('"%UID"', str(self.env.user.id))

        if domain and "%MYCOMPANY" in domain:
            domain = domain.replace('"%MYCOMPANY"', str(self.env.user.company_id.id))

        date_domain = False

        if (
            not dashboard_rec.date_domain_fields
            or dashboard_rec.date_domain_fields == "none"
        ):
            selected_start_date = self._context.get("DateFilterStartDate", False)
            selected_end_date = self._context.get("DateFilterEndDate", False)
            if (
                selected_start_date
                and selected_end_date
                and dashboard_rec.date_filter_field.name
            ):
                date_domain = [
                    (
                        dashboard_rec.date_filter_field.name,
                        ">=",
                        selected_start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    ),
                    (
                        dashboard_rec.date_filter_field.name,
                        "<=",
                        selected_end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    ),
                ]
        else:
            if (
                dashboard_rec.date_domain_fields
                and dashboard_rec.date_domain_fields != "last_custom"
            ):
                filter_date_value = generate_date(dashboard_rec.date_domain_fields)
                selected_start_date = filter_date_value["selected_start_date"]
                selected_end_date = filter_date_value["selected_end_date"]
            else:
                if dashboard_rec.element_start_date or dashboard_rec.element_end_date:
                    selected_start_date = dashboard_rec.element_start_date
                    selected_end_date = dashboard_rec.element_end_date

            if selected_start_date and selected_end_date:
                if dashboard_rec.time_of_comparation:
                    time_of_comparation = abs(dashboard_rec.time_of_comparation)
                    if time_of_comparation > 100:
                        time_of_comparation = 100
                    if dashboard_rec.time_of_comparation > 0:
                        selected_end_date = (
                            selected_end_date
                            + (selected_end_date - selected_start_date)
                            * time_of_comparation
                        )
                    elif dashboard_rec.time_of_comparation < 0:
                        selected_start_date = (
                            selected_start_date
                            - (selected_end_date - selected_start_date)
                            * time_of_comparation
                        )

                if (
                    dashboard_rec.year_period
                    and dashboard_rec.year_period != 0
                    and dashboard_rec.type_of_element
                ):
                    abs_year_period = abs(dashboard_rec.year_period)
                    sign_yp = dashboard_rec.year_period / abs_year_period
                    if abs_year_period > 10:
                        abs_year_period = 10
                    date_field_name = dashboard_rec.date_filter_field.name

                    date_domain = [
                        "&",
                        (
                            date_field_name,
                            ">=",
                            fields.datetime.strftime(
                                selected_start_date, DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        ),
                        (
                            date_field_name,
                            "<=",
                            fields.datetime.strftime(
                                selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        ),
                    ]

                    for p in range(1, abs_year_period + 1):
                        date_domain.insert(0, "|")
                        date_domain.extend(
                            [
                                "&",
                                (
                                    date_field_name,
                                    ">=",
                                    fields.datetime.strftime(
                                        selected_start_date
                                        - relativedelta.relativedelta(years=p)
                                        * sign_yp,
                                        DEFAULT_SERVER_DATETIME_FORMAT,
                                    ),
                                ),
                                (
                                    date_field_name,
                                    "<=",
                                    fields.datetime.strftime(
                                        selected_end_date
                                        - relativedelta.relativedelta(years=p)
                                        * sign_yp,
                                        DEFAULT_SERVER_DATETIME_FORMAT,
                                    ),
                                ),
                            ]
                        )
                else:
                    if dashboard_rec.date_filter_field:
                        selected_start_date = fields.datetime.strftime(
                            selected_start_date, DEFAULT_SERVER_DATETIME_FORMAT
                        )
                        selected_end_date = fields.datetime.strftime(
                            selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT
                        )
                        date_domain = [
                            (
                                dashboard_rec.date_filter_field.name,
                                ">=",
                                selected_start_date,
                            ),
                            (
                                dashboard_rec.date_filter_field.name,
                                "<=",
                                selected_end_date,
                            ),
                        ]
                    else:
                        date_domain = []

        proper_domain = eval(domain) if domain else []
        if date_domain:
            proper_domain.extend(date_domain)

        return proper_domain

    @api.depends(
        "type_of_element",
        "is_goal_enable",
        "goal_value_field",
        "data_calculation_value",
        "record_count_2",
        "previous_data_field",
        "time_of_comparation",
        "year_period",
        "time_of_comparation_2",
        "year_period_2",
    )
    def _compute_kpi_info_func(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.type_of_element
                and dashboard_rec.type_of_element == "kpi"
                and dashboard_rec.model_id
            ):
                kpi_data = []
                data_calculation_value = 0.0
                kpi_data_model_1 = {}
                data_calculation_value = dashboard_rec.data_calculation_value
                kpi_data_model_1["model"] = dashboard_rec.model_name
                kpi_data_model_1[
                    "store_field_data"
                ] = dashboard_rec.store_field_data.field_description
                kpi_data_model_1["record_data"] = data_calculation_value

                if dashboard_rec.is_goal_enable:
                    kpi_data_model_1["target"] = dashboard_rec.goal_value_field
                kpi_data.append(kpi_data_model_1)

                if dashboard_rec.previous_data_field:
                    previous_period_data = dashboard_rec.filter_previous_data_func(
                        dashboard_rec
                    )
                    kpi_data_model_1["previous_data_field"] = previous_period_data

                if (
                    dashboard_rec.ir_model_field_2
                    and dashboard_rec.data_calculation_type
                ):
                    kpi_data_model_2 = {}
                    kpi_data_model_2["model"] = dashboard_rec.ir_model_field_2_name
                    kpi_data_model_2["store_field_data"] = (
                        "count"
                        if dashboard_rec.data_calculation_type == "count"
                        else dashboard_rec.store_field_data_2.field_description
                    )
                    kpi_data_model_2["record_data"] = dashboard_rec.record_count_2
                    kpi_data.append(kpi_data_model_2)

                dashboard_rec.kpi_data = json.dumps(kpi_data)
            else:
                dashboard_rec.kpi_data = False

    def filter_previous_data_func(self, dashboard_rec):
        switcher = {
            "last_day": "generate_date('lastp_day')",
            "this_week": "generate_date('lastp_week')",
            "this_month": "generate_date('lastp_month')",
            "this_quarter": "generate_date('lastp_quarter')",
            "this_year": "generate_date('lastp_year')",
        }

        if dashboard_rec.date_domain_fields == "none":
            date_domain_fields = (
                dashboard_rec.dashboard_pro_dashboard_id.date_domain_fields
            )
        else:
            date_domain_fields = dashboard_rec.date_domain_fields
        filter_date_value = eval(switcher.get(date_domain_fields, "False"))

        if filter_date_value:
            previous_period_start_date = filter_date_value["selected_start_date"]
            previous_period_end_date = filter_date_value["selected_end_date"]
            proper_domain = dashboard_rec.domain_previous_func(
                dashboard_rec.domain,
                previous_period_start_date,
                previous_period_end_date,
                dashboard_rec.date_filter_field,
            )
            data_calculation_value = 0.0

            if dashboard_rec.data_calculation_type == "count":
                data_calculation_value = self.env[
                    dashboard_rec.model_name
                ].search_count(proper_domain)
                return data_calculation_value
            elif dashboard_rec.store_field_data:
                data = self.env[dashboard_rec.model_name].read_group(
                    proper_domain, [dashboard_rec.store_field_data.name], []
                )[0]
                if dashboard_rec.data_calculation_type == "sum":
                    return (
                        data.get(dashboard_rec.store_field_data.name, 0)
                        if data.get("__count", False)
                        and (data.get(dashboard_rec.store_field_data.name))
                        else 0
                    )
                else:
                    return (
                        data.get(dashboard_rec.store_field_data.name, 0)
                        / data.get("__count", 1)
                        if data.get("__count", False)
                        and (data.get(dashboard_rec.store_field_data.name))
                        else 0
                    )
            else:
                return False
        else:
            return False

    @api.onchange("ir_model_field_2")
    def record_empty_func_2(self):
        for dashboard_rec in self:
            dashboard_rec.store_field_data_2 = False
            dashboard_rec.domain_2 = False
            dashboard_rec.date_filter_field_2 = False
            if dashboard_rec.model_id:
                datetime_field_list = dashboard_rec.date_filter_field_2.search(
                    [
                        ("model_id", "=", dashboard_rec.model_id.id),
                        "|",
                        ("ttype", "=", "date"),
                        ("ttype", "=", "datetime"),
                    ]
                ).read(["id", "name"])
                for field in datetime_field_list:
                    if field["name"] == "create_date":
                        dashboard_rec.date_filter_field_2 = field["id"]
            else:
                dashboard_rec.date_filter_field_2 = False

    def domain_previous_func(self, domain, start_date, end_date, date_filter_field):
        if domain and "%UID" in domain:
            domain = domain.replace('"%UID"', str(self.env.user.id))
        if domain:
            proper_domain = eval(domain)
            if start_date and end_date and date_filter_field:
                proper_domain.extend(
                    [
                        (date_filter_field.name, ">=", start_date),
                        (date_filter_field.name, "<=", end_date),
                    ]
                )

        else:
            if start_date and end_date and date_filter_field:
                proper_domain = [
                    (date_filter_field.name, ">=", start_date),
                    (date_filter_field.name, "<=", end_date),
                ]
            else:
                proper_domain = []
        return proper_domain

    @api.depends(
        "domain_2",
        "ir_model_field_2",
        "store_field_data_2",
        "data_calculation_type",
        "starting_date_kpi_2",
        "date_filter_selection_2",
        "data_calculation_type",
        "time_of_comparation_2",
        "year_period_2",
    )
    def _compute_data_calculation_func_1(self):
        for dashboard_rec in self:
            if dashboard_rec.data_calculation_type == "count":
                data_calculation_value = dashboard_rec.getting_data_of_model_2(
                    dashboard_rec.ir_model_field_2_name,
                    dashboard_rec.domain_2,
                    "search_count",
                    dashboard_rec,
                )

            elif (
                dashboard_rec.data_calculation_type in ["sum", "average"]
                and dashboard_rec.store_field_data_2
            ):
                records_grouped_data = dashboard_rec.getting_data_of_model_2(
                    dashboard_rec.ir_model_field_2_name,
                    dashboard_rec.domain_2,
                    "read_group",
                    dashboard_rec,
                )
                if records_grouped_data and len(records_grouped_data) > 0:
                    records_grouped_data = records_grouped_data[0]
                    if (
                        dashboard_rec.data_calculation_type == "sum"
                        and records_grouped_data.get("__count", False)
                        and (
                            records_grouped_data.get(
                                dashboard_rec.store_field_data_2.name
                            )
                        )
                    ):
                        data_calculation_value = records_grouped_data.get(
                            dashboard_rec.store_field_data_2.name, 0
                        )
                    elif (
                        dashboard_rec.data_calculation_type == "average"
                        and records_grouped_data.get("__count", False)
                        and (
                            records_grouped_data.get(
                                dashboard_rec.store_field_data_2.name
                            )
                        )
                    ):
                        data_calculation_value = records_grouped_data.get(
                            dashboard_rec.store_field_data_2.name, 0
                        ) / records_grouped_data.get("__count", 1)
                    else:
                        data_calculation_value = 0
                else:
                    data_calculation_value = 0
            else:
                data_calculation_value = False

            dashboard_rec.record_count_2 = data_calculation_value

    def getting_data_of_model_2(self, model_name, domain, func, dashboard_rec):
        data = 0
        try:
            if domain and domain != "[]" and model_name:
                proper_domain = self.domain_conversion_func(domain, dashboard_rec)
                if func == "search_count":
                    data = self.env[model_name].search_count(proper_domain)
                elif func == "read_group":
                    data = self.env[model_name].read_group(
                        proper_domain, [dashboard_rec.store_field_data_2.name], []
                    )
            elif model_name:
                proper_domain = self.domain_conversion_func(False, dashboard_rec)
                if func == "search_count":
                    data = self.env[model_name].search_count(proper_domain)

                elif func == "read_group":
                    data = self.env[model_name].read_group(
                        proper_domain, [dashboard_rec.store_field_data_2.name], []
                    )
            else:
                return []
        except Exception:
            return []
        return data

    def domain_conversion_func(self, domain_2, dashboard_rec):
        if domain_2 and "%UID" in domain_2:
            domain_2 = domain_2.replace('"%UID"', str(self.env.user.id))
        if domain_2 and "%MYCOMPANY" in domain_2:
            domain_2 = domain_2.replace(
                '"%MYCOMPANY"', str(self.env.user.company_id.id)
            )

        date_domain = False

        if (
            not dashboard_rec.date_filter_selection_2
            or dashboard_rec.date_filter_selection_2 == "none"
        ):
            selected_start_date = self._context.get("DateFilterStartDate", False)
            selected_end_date = self._context.get("DateFilterEndDate", False)
            if (
                selected_start_date
                and selected_end_date
                and dashboard_rec.date_filter_field_2.name
            ):
                date_domain = [
                    (
                        dashboard_rec.date_filter_field_2.name,
                        ">=",
                        selected_start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    ),
                    (
                        dashboard_rec.date_filter_field_2.name,
                        "<=",
                        selected_end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    ),
                ]
        else:
            if (
                dashboard_rec.date_filter_selection_2
                and dashboard_rec.date_filter_selection_2 != "last_custom"
            ):
                filter_date_value = generate_date(dashboard_rec.date_filter_selection_2)
                selected_start_date = filter_date_value["selected_start_date"]
                selected_end_date = filter_date_value["selected_end_date"]
            else:
                if dashboard_rec.starting_date_kpi_2 or dashboard_rec.ending_date_kpi_2:
                    selected_start_date = dashboard_rec.element_start_date
                    selected_end_date = dashboard_rec.element_end_date

            if selected_start_date and selected_end_date:
                if dashboard_rec.time_of_comparation_2:
                    time_of_comparation_2 = abs(dashboard_rec.time_of_comparation_2)
                    if time_of_comparation_2 > 100:
                        time_of_comparation_2 = 100
                    if dashboard_rec.time_of_comparation_2 > 0:
                        selected_end_date = (
                            selected_end_date
                            + (selected_end_date - selected_start_date)
                            * time_of_comparation_2
                        )
                    elif dashboard_rec.time_of_comparation_2 < 0:
                        selected_start_date = (
                            selected_start_date
                            - (selected_end_date - selected_start_date)
                            * time_of_comparation_2
                        )

                if dashboard_rec.year_period_2 and dashboard_rec.year_period_2 != 0:
                    abs_year_period_2 = abs(dashboard_rec.year_period_2)
                    sign_yp = dashboard_rec.year_period_2 / abs_year_period_2
                    if abs_year_period_2 > 10:
                        abs_year_period_2 = 10
                    date_field_name = dashboard_rec.date_filter_field_2.name

                    date_domain = [
                        "&",
                        (
                            date_field_name,
                            ">=",
                            fields.datetime.strftime(
                                selected_start_date, DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        ),
                        (
                            date_field_name,
                            "<=",
                            fields.datetime.strftime(
                                selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        ),
                    ]

                    for p in range(1, abs_year_period_2 + 1):
                        date_domain.insert(0, "|")
                        date_domain.extend(
                            [
                                "&",
                                (
                                    date_field_name,
                                    ">=",
                                    fields.datetime.strftime(
                                        selected_start_date
                                        - relativedelta.relativedelta(years=p)
                                        * sign_yp,
                                        DEFAULT_SERVER_DATETIME_FORMAT,
                                    ),
                                ),
                                (
                                    date_field_name,
                                    "<=",
                                    fields.datetime.strftime(
                                        selected_end_date
                                        - relativedelta.relativedelta(years=p)
                                        * sign_yp,
                                        DEFAULT_SERVER_DATETIME_FORMAT,
                                    ),
                                ),
                            ]
                        )
                else:
                    if dashboard_rec.date_filter_field_2:
                        selected_start_date = fields.datetime.strftime(
                            selected_start_date, DEFAULT_SERVER_DATETIME_FORMAT
                        )
                        selected_end_date = fields.datetime.strftime(
                            selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT
                        )
                        date_domain = [
                            (
                                dashboard_rec.date_filter_field_2.name,
                                ">=",
                                selected_start_date,
                            ),
                            (
                                dashboard_rec.date_filter_field_2.name,
                                "<=",
                                selected_end_date,
                            ),
                        ]
                    else:
                        date_domain = []

        proper_domain = eval(domain_2) if domain_2 else []
        if date_domain:
            proper_domain.extend(date_domain)

        return proper_domain

    def chart_data_sub_func(
        self,
        model_name,
        chart_domain,
        chart_data_calculation_field,
        chart_data_calculation_field_2,
        chart_groupby_relation_field,
        chart_group_field,
        group_chart_field,
        orderby,
        limit,
        chart_count,
        chart_measure_field_ids,
        chart_measure_field_2_ids,
        chart_groupby_relation_field_id,
        chart_data,
    ):

        if group_chart_field == "date_type":
            chart_groupby_field = chart_groupby_relation_field + ":" + chart_group_field
        else:
            chart_groupby_field = chart_groupby_relation_field

        try:
            chart_records = self.env[model_name].read_group(
                chart_domain,
                set(
                    chart_data_calculation_field
                    + chart_data_calculation_field_2
                    + [chart_groupby_relation_field]
                ),
                [chart_groupby_field],
                orderby=orderby,
                limit=limit,
            )
        except Exception:
            chart_records = []
        chart_data["groupby"] = chart_groupby_field
        if group_chart_field == "relational_type":
            chart_data["groupByIds"] = []

        for res in chart_records:

            if all(
                measure_field in res for measure_field in chart_data_calculation_field
            ):
                if group_chart_field == "relational_type":
                    if res[chart_groupby_field]:
                        chart_data["labels"].append(res[chart_groupby_field][1]._value)
                        chart_data["groupByIds"].append(res[chart_groupby_field][0])
                    else:
                        chart_data["labels"].append(res[chart_groupby_field])
                elif group_chart_field == "selection":
                    selection = res[chart_groupby_field]
                    if selection:
                        chart_data["labels"].append(
                            dict(
                                self.env[model_name].fields_get(
                                    allfields=[chart_groupby_field]
                                )[chart_groupby_field]["selection"]
                            )[selection]
                        )
                    else:
                        chart_data["labels"].append(selection)
                else:
                    chart_data["labels"].append(res[chart_groupby_field])
                chart_data["domains"].append(res.get("__domain", []))

                counter = 0
                if chart_data_calculation_field:
                    if chart_data_calculation_field_2:
                        index = 0
                        for field_rec in chart_data_calculation_field_2:
                            groupby_equal_measures = (
                                res[chart_groupby_relation_field + "_count"]
                                if chart_measure_field_2_ids[index]
                                == chart_groupby_relation_field_id
                                else 1
                            )
                            data = (
                                res[field_rec] * groupby_equal_measures
                                if chart_count == "sum"
                                else res[field_rec]
                                * groupby_equal_measures
                                / res[chart_groupby_relation_field + "_count"]
                            )
                            chart_data["datasets"][counter]["data"].append(data)
                            counter += 1
                            index += 1

                    index = 0
                    for field_rec in chart_data_calculation_field:
                        groupby_equal_measures = (
                            res[chart_groupby_relation_field + "_count"]
                            if chart_measure_field_ids[index]
                            == chart_groupby_relation_field_id
                            else 1
                        )
                        data = (
                            res[field_rec] * groupby_equal_measures
                            if chart_count == "sum"
                            else res[field_rec]
                            * groupby_equal_measures
                            / res[chart_groupby_relation_field + "_count"]
                        )
                        chart_data["datasets"][counter]["data"].append(data)
                        counter += 1
                        index += 1

                else:
                    data = res[chart_groupby_relation_field + "_count"]
                    chart_data["datasets"][0]["data"].append(data)

        return chart_data

    @api.depends("chart_sub_field")
    def _compute_chart_group_type_func(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.chart_sub_field.ttype == "datetime"
                or dashboard_rec.chart_sub_field.ttype == "date"
            ):
                dashboard_rec.sub_group_chart_field = "date_type"
            elif dashboard_rec.chart_sub_field.ttype == "many2one":
                dashboard_rec.sub_group_chart_field = "relational_type"

            elif dashboard_rec.chart_sub_field.ttype == "selection":
                dashboard_rec.sub_group_chart_field = "selection"

            else:
                dashboard_rec.sub_group_chart_field = "other"

    @api.model
    def get_sorted_month(self, display_format, ftype="date"):
        query = """
                        with d as (SELECT date_trunc(%(aggr)s, generate_series)
                        AS timestamp FROM generate_series
                        (%(timestamp_begin)s::TIMESTAMP ,
                        %(timestamp_end)s::TIMESTAMP , %(aggr1)s::interval ))
                         select timestamp from d group by timestamp order by timestamp
                            """
        self.env.cr.execute(
            query,
            {
                "timestamp_begin": "2020-01-01 00:00:00",
                "timestamp_end": "2020-12-31 00:00:00",
                "aggr": "month",
                "aggr1": "1 month",
            },
        )

        dates = self.env.cr.fetchall()
        locale = self._context.get("lang") or "en_US"
        tz_convert = self._context.get("tz")
        return [
            self.format_label(d[0], ftype, display_format, tz_convert, locale)
            for d in dates
        ]

    @api.model
    def create_time_pattern_func(self, date_begin, date_end, aggr, ftype="date"):
        query = """
                        with d as (SELECT date_trunc(%(aggr)s, generate_series) AS
                        timestamp FROM generate_series
                        (%(timestamp_begin)s::TIMESTAMP ,
                        %(timestamp_end)s::TIMESTAMP , '1 hour'::interval ))
                        select timestamp from d group by timestamp order by timestamp
                    """

        self.env.cr.execute(
            query,
            {
                "timestamp_begin": date_begin,
                "timestamp_end": date_end,
                "aggr": aggr,
                "aggr1": "1 " + aggr,
            },
        )
        dates = self.env.cr.fetchall()
        display_formats = {
            "minute": "hh:mm dd MMM",
            "hour": "hh:00 dd MMM",
            "day": "dd MMM yyyy",
            "week": "'W'w YYYY",
            "month": "MMMM yyyy",
            "quarter": "QQQ yyyy",
            "year": "yyyy",
        }

        display_format = display_formats[aggr]
        locale = self._context.get("lang") or "en_US"
        tz_convert = self._context.get("tz")
        return [
            self.format_label(d[0], ftype, display_format, tz_convert, locale)
            for d in dates
        ]

    @api.model
    def format_label(self, value, ftype, display_format, tz_convert, locale):

        tzinfo = None
        if ftype == "datetime":

            if tz_convert:
                value = pytz.timezone(self._context["tz"]).localize(value)
                tzinfo = value.tzinfo
            return babel.dates.format_datetime(
                value, format=display_format, tzinfo=tzinfo, locale=locale
            )
        else:

            if tz_convert:
                value = pytz.timezone(self._context["tz"]).localize(value)
                tzinfo = value.tzinfo
            return babel.dates.format_date(value, format=display_format, locale=locale)

    @api.onchange("domain_2")
    def domain_onchange_func(self):
        if self.domain_2:
            proper_domain_2 = []
            try:
                domain_2 = self.domain_2
                if "%UID" in domain_2:
                    domain_2 = domain_2.replace("%UID", str(self.env.user.id))
                if "%MYCOMPANY" in domain_2:
                    domain_2 = domain_2.replace(
                        "%MYCOMPANY", str(self.env.user.company_id.id)
                    )
                domain_2 = safe_eval(domain_2)

                for element in domain_2:
                    proper_domain_2.append(element) if type(
                        element
                    ) != list else proper_domain_2.append(tuple(element))
                self.env[self.ir_model_field_2_name].search_count(proper_domain_2)
            except Exception:
                raise UserError(_("Invalid Domain"))

    @api.onchange("domain")
    def domain_onchange_func_2(self):
        if self.domain:
            proper_domain = []
            try:
                domain = self.domain
                if "%UID" in domain:
                    domain = domain.replace("%UID", str(self.env.user.id))
                if "%MYCOMPANY" in domain:
                    domain = domain.replace(
                        "%MYCOMPANY", str(self.env.user.company_id.id)
                    )
                domain = safe_eval(domain)
                for element in domain:
                    proper_domain.append(element) if type(
                        element
                    ) != list else proper_domain.append(tuple(element))
                self.env[self.model_name].search_count(proper_domain)
            except Exception:
                raise UserError(_("Invalid Domain"))

    def gropu_data_sort_func(
        self,
        data,
        field_type,
        chart_group_field,
        sorting_selection,
        chart_sub_field_date,
    ):
        if data:
            reverse = False
            if sorting_selection == "DESC":
                reverse = True

            for data in data:
                if field_type == "date_type":
                    if chart_group_field in ["minute", "hour"]:
                        if chart_sub_field_date in ["month", "week", "quarter", "year"]:
                            sorted_months = self.get_sorted_month("MMM")
                            data["value"].sort(
                                key=lambda x: int(
                                    str(sorted_months.index(x["x"].split(" ")[2]) + 1)
                                    + x["x"].split(" ")[1]
                                    + x["x"].split(" ")[0].replace(":", "")
                                ),
                                reverse=reverse,
                            )
                        else:
                            data["value"].sort(
                                key=lambda x: int(x["x"].replace(":", "")),
                                reverse=reverse,
                            )
                    elif chart_group_field == "day" and chart_sub_field_date in [
                        "quarter",
                        "year",
                    ]:
                        sorted_days = self.create_time_pattern_func(
                            "2020-01-01 00:00:00", "2020-12-31 00:00:00", "day", "date"
                        )
                        b = [" ".join(x.split(" ")[0:2]) for x in sorted_days]
                        data["value"].sort(
                            key=lambda x: b.index(x["x"]), reverse=reverse
                        )
                    elif chart_group_field == "day" and chart_sub_field_date not in [
                        "quarter",
                        "year",
                    ]:
                        data["value"].sort(key=lambda i: int(i["x"]), reverse=reverse)
                    elif chart_group_field == "week":
                        data["value"].sort(
                            key=lambda i: int(i["x"][1:]), reverse=reverse
                        )
                    elif chart_group_field == "month":
                        sorted_months = self.create_time_pattern_func(
                            "2020-01-01 00:00:00",
                            "2020-12-31 00:00:00",
                            "month",
                            "date",
                        )
                        b = [" ".join(x.split(" ")[0:1]) for x in sorted_months]
                        data["value"].sort(
                            key=lambda x: b.index(x["x"]), reverse=reverse
                        )
                    elif chart_group_field == "quarter":
                        sorted_months = self.create_time_pattern_func(
                            "2020-01-01 00:00:00",
                            "2020-12-31 00:00:00",
                            "quarter",
                            "date",
                        )
                        b = [" ".join(x.split(" ")[:-1]) for x in sorted_months]
                        data["value"].sort(
                            key=lambda x: b.index(x["x"]), reverse=reverse
                        )
                    elif chart_group_field == "year":
                        data["value"].sort(key=lambda i: int(i["x"]), reverse=reverse)
                else:
                    data["value"].sort(key=lambda i: i["x"], reverse=reverse)

        return data

    @api.onchange("model_id")
    def data_record_empty_func(self):
        for dashboard_rec in self:
            dashboard_rec.store_field_data = False
            dashboard_rec.domain = False
            dashboard_rec.date_filter_field = False
            if dashboard_rec.model_id:
                datetime_field_list = dashboard_rec.date_filter_field.search(
                    [
                        ("model_id", "=", dashboard_rec.model_id.id),
                        "|",
                        ("ttype", "=", "date"),
                        ("ttype", "=", "datetime"),
                    ]
                ).read(["id", "name"])
                for field in datetime_field_list:
                    if field["name"] == "create_date":
                        dashboard_rec.date_filter_field = field["id"]
            else:
                dashboard_rec.date_filter_field = False
            dashboard_rec.store_field_data = False
            dashboard_rec.chart_data_calculation_field = False
            dashboard_rec.chart_data_calculation_field_2 = False
            dashboard_rec.chart_sub_field = False
            dashboard_rec.group_chart_relation = False
            dashboard_rec.chart_sub_field_date = False
            dashboard_rec.chart_group_field = False
            dashboard_rec.sorting_selection_by_field = False
            dashboard_rec.sorting_selection = False
            dashboard_rec.filter_limit = False
            dashboard_rec.list_fields_data = False
            dashboard_rec.list_data_grouping = False
            dashboard_rec.action_lines = False
            dashboard_rec.actions = False

    @api.onchange("element_theme")
    def dashboard_element_theme_func(self):
        if self.element_theme == "red":
            self.background_color = "#d9534f,0.99"
            self.default_icon_color = "#ffffff,0.99"
            self.font_color = "#ffffff,0.99"

        elif self.element_theme == "blue":
            self.background_color = "#337ab7,0.99"
            self.default_icon_color = "#ffffff,0.99"
            self.font_color = "#ffffff,0.99"

        elif self.element_theme == "yellow":
            self.background_color = "#f0ad4e,0.99"
            self.default_icon_color = "#ffffff,0.99"
            self.font_color = "#ffffff,0.99"

        elif self.element_theme == "green":
            self.background_color = "#5cb85c,0.99"
            self.default_icon_color = "#ffffff,0.99"
            self.font_color = "#ffffff,0.99"

        elif self.element_theme == "white":
            if self.layout == "layout4":
                self.background_color = "#00000,0.99"
                self.default_icon_color = "#ffffff,0.99"

            else:
                self.background_color = "#ffffff,0.99"
                self.default_icon_color = "#000000,0.99"
                self.font_color = "#000000,0.99"

        if self.layout == "layout4":
            self.font_color = self.background_color

        elif self.layout == "layout6":
            self.default_icon_color = self.dark_color_generator(
                self.background_color.split(",")[0], self.background_color.split(",")[1]
            )
            if self.element_theme == "white":
                self.default_icon_color = "#000000,0.99"

    def dark_color_generator(self, color, opacity):
        num = int(color[1:], 16)
        amt = -25
        R = (num >> 16) + amt
        R = (255 if R > 255 else 0 if R < 0 else R) * 0x10000
        G = (num >> 8 & 0x00FF) + amt
        G = (255 if G > 255 else 0 if G < 0 else G) * 0x100
        B = (num & 0x0000FF) + amt
        B = 255 if B > 255 else 0 if B < 0 else B
        return "#" + hex(0x1000000 + R + G + B).split("x")[1][1:] + "," + opacity

    @api.model
    def get_data_main_func(self, element_id, domain, sequence):

        record = self.browse(int(element_id))
        chart_data = {
            "labels": [],
            "datasets": [],
            "show_second_y_scale": False,
            "domains": [],
            "previous_domain": domain,
            "currency": 0,
            "field": "",
            "selection": "",
        }
        if record.unit and record.unit_selection == "monetary":
            chart_data["selection"] += record.unit_selection
            chart_data["currency"] += record.env.user.company_id.currency_id.id
        elif record.unit and record.unit_selection == "custom":
            chart_data["selection"] += record.unit_selection
            if record.chart_unit:
                chart_data["field"] += record.chart_unit

        action_lines = record.action_lines.sorted(key=lambda r: r.sequence)
        action_line = action_lines[sequence]
        chart_type = (
            action_line.chart_type if action_line.chart_type else record.type_of_element
        )
        json_list_data = {
            "label": [],
            "type": "grouped",
            "data_rows": [],
            "model": record.model_name,
            "previous_domain": domain,
        }
        if action_line.chart_type == "list_view":
            if record.type_of_element == "list_view":
                chart_list_measure = record.list_data_grouping
            else:
                chart_list_measure = record.chart_data_calculation_field

            list_fields = []
            orderby = (
                action_line.sorting_selection_by_field.name
                if action_line.sorting_selection_by_field
                else "id"
            )
            if action_line.sorting_selection:
                orderby = orderby + " " + action_line.sorting_selection
            limit = (
                action_line.record_limit
                if action_line.record_limit and action_line.record_limit > 0
                else False
            )
            count = 0
            for pro in record.action_lines: # noqa
                count += 1
            if action_line.item_action_field.ttype == "many2one":
                json_list_data["groupby"] = action_line.item_action_field.name
                list_fields.append(action_line.item_action_field.name)
                json_list_data["label"].append(
                    action_line.item_action_field.field_description
                )
                for res in chart_list_measure:
                    list_fields.append(res.name)
                    json_list_data["label"].append(res.field_description)

                list_view_records = self.env[record.model_name].read_group(
                    domain,
                    list_fields,
                    [action_line.item_action_field.name],
                    orderby=orderby,
                    limit=limit,
                )
                for res in list_view_records:

                    counter = 0
                    data_row = {
                        "id": res[action_line.item_action_field.name][0],
                        "data": [],
                        "domain": json.dumps(res["__domain"]),
                        "sequence": sequence + 1,
                        "last_seq": count,
                    }
                    for field_rec in list_fields:
                        if counter == 0:
                            data_row["data"].append(res[field_rec][1]._value)
                        else:
                            data_row["data"].append(res[field_rec])
                        counter += 1
                    json_list_data["data_rows"].append(data_row)

            elif (
                action_line.item_action_field.ttype == "date"
                or action_line.item_action_field.ttype == "datetime"
            ):
                json_list_data["list_view_type"] = "date_type"
                list_field = []
                json_list_data["groupby"] = (
                    action_line.item_action_field.name
                    + ":"
                    + action_line.item_action_date_groupby
                )
                list_field.append(
                    action_line.item_action_field.name
                    + ":"
                    + action_line.item_action_date_groupby
                )
                list_fields.append(action_line.item_action_field.name)
                json_list_data["label"].append(
                    action_line.item_action_field.field_description
                )
                for res in chart_list_measure:
                    list_fields.append(res.name)
                    list_field.append(res.name)
                    json_list_data["label"].append(res.field_description)

                list_view_records = self.env[record.model_name].read_group(
                    domain,
                    list_fields,
                    [
                        action_line.item_action_field.name
                        + ":"
                        + action_line.item_action_date_groupby
                    ],
                    orderby=orderby,
                    limit=limit,
                )

                for res in list_view_records:
                    counter = 0
                    data_row = {
                        "data": [],
                        "domain": json.dumps(res["__domain"]),
                        "sequence": sequence + 1,
                        "last_seq": count,
                    }
                    for field_rec in list_field:
                        data_row["data"].append(res[field_rec])
                    json_list_data["data_rows"].append(data_row)

            elif action_line.item_action_field.ttype == "selection":
                json_list_data["list_view_type"] = "selection"
                json_list_data["groupby"] = action_line.item_action_field.name
                selection_field = action_line.item_action_field.name
                json_list_data["label"].append(
                    action_line.item_action_field.field_description
                )
                for res in chart_list_measure:
                    list_fields.append(res.name)
                    json_list_data["label"].append(res.field_description)

                list_view_records = self.env[record.model_name].read_group(
                    domain,
                    list_fields,
                    [action_line.item_action_field.name],
                    orderby=orderby,
                    limit=limit,
                )
                for res in list_view_records:
                    counter = 0
                    data_row = {
                        "data": [],
                        "domain": json.dumps(res["__domain"]),
                        "sequence": sequence + 1,
                        "last_seq": count,
                    }
                    if res[selection_field]:
                        data_row["data"].append(
                            dict(
                                self.env[record.model_name].fields_get(
                                    allfields=selection_field
                                )[selection_field]["selection"]
                            )[res[selection_field]]
                        )
                    else:
                        data_row["data"].append(" ")
                    for field_rec in list_fields:
                        data_row["data"].append(res[field_rec])
                    json_list_data["data_rows"].append(data_row)

            else:
                json_list_data["list_view_type"] = "other"
                json_list_data["groupby"] = action_line.item_action_field.name
                list_fields.append(action_line.item_action_field.name)
                json_list_data["label"].append(
                    action_line.item_action_field.field_description
                )
                for res in chart_list_measure:
                    list_fields.append(res.name)
                    json_list_data["label"].append(res.field_description)

                list_view_records = self.env[record.model_name].read_group(
                    domain,
                    list_fields,
                    [action_line.item_action_field.name],
                    orderby=orderby,
                    limit=limit,
                )
                for res in list_view_records:
                    if all(list_fields in res for list_fields in list_fields):
                        counter = 0
                        data_row = {
                            "id": action_line.item_action_field.name,
                            "data": [],
                            "domain": json.dumps(res["__domain"]),
                            "sequence": sequence + 1,
                            "last_seq": count,
                        }

                        for field_rec in list_fields:
                            if counter == 0:
                                data_row["data"].append(res[field_rec])
                            else:
                                if action_line.item_action_field.name == field_rec:
                                    data_row["data"].append(
                                        res[field_rec] * res[field_rec + "_count"]
                                    )
                                else:
                                    data_row["data"].append(res[field_rec])
                            counter += 1
                        json_list_data["data_rows"].append(data_row)

            return {
                "json_list_data": json.dumps(json_list_data),
                "list_view_type": "grouped",
                "sequence": sequence + 1,
            }
        else:
            chart_data_calculation_field = []
            chart_measure_field_ids = []
            chart_data_calculation_field_2 = []
            chart_measure_field_2_ids = []
            if record.data_calculation_type_chart == "count":
                chart_data["datasets"].append({"data": [], "label": "Count"})
            else:
                if chart_type == "bar_chart":
                    if record.chart_data_calculation_field_2:
                        chart_data["show_second_y_scale"] = True

                    for res in record.chart_data_calculation_field_2:
                        chart_data_calculation_field_2.append(res.name)
                        chart_measure_field_2_ids.append(res.id)
                        chart_data["datasets"].append(
                            {
                                "data": [],
                                "label": res.field_description,
                                "type": "line",
                                "yAxisID": "y-axis-1",
                            }
                        )
                if record.type_of_element == "list_view":
                    for res in record.list_data_grouping:
                        chart_data_calculation_field.append(res.name)
                        chart_measure_field_ids.append(res.id)
                        chart_data["datasets"].append(
                            {"data": [], "label": res.field_description}
                        )
                else:
                    for res in record.chart_data_calculation_field:
                        chart_data_calculation_field.append(res.name)
                        chart_measure_field_ids.append(res.id)
                        chart_data["datasets"].append(
                            {"data": [], "label": res.field_description}
                        )

            chart_groupby_relation_field = action_line.item_action_field.name
            chart_relation_type = action_line.item_action_field_type
            chart_date_group_by = action_line.item_action_date_groupby
            chart_groupby_relation_field_id = action_line.item_action_field.id
            orderby = (
                action_line.sorting_selection_by_field.name
                if action_line.sorting_selection_by_field
                else "id"
            )
            if action_line.sorting_selection:
                orderby = orderby + " " + action_line.sorting_selection
            limit = (
                action_line.record_limit
                if action_line.record_limit and action_line.record_limit > 0
                else False
            )

            if chart_type != "bar_chart":
                chart_data_calculation_field_2 = []
                chart_measure_field_2_ids = []

            chart_data = record.chart_data_sub_func(
                record.model_name,
                domain,
                chart_data_calculation_field,
                chart_data_calculation_field_2,
                chart_groupby_relation_field,
                chart_date_group_by,
                chart_relation_type,
                orderby,
                limit,
                record.data_calculation_type_chart,
                chart_measure_field_ids,
                chart_measure_field_2_ids,
                chart_groupby_relation_field_id,
                chart_data,
            )

            return {
                "chart_data": json.dumps(chart_data),
                "chart_type": chart_type,
                "sequence": sequence + 1,
            }

    @api.onchange("date_domain_fields")
    def date_filter_func(self):
        for dashboard_rec in self:
            if (
                not dashboard_rec.date_domain_fields
            ) or dashboard_rec.date_domain_fields == "none":
                dashboard_rec.element_start_date = (
                    dashboard_rec.element_end_date
                ) = False
            elif dashboard_rec.date_domain_fields != "last_custom":
                filter_date_value = generate_date(dashboard_rec.date_domain_fields)
                dashboard_rec.element_start_date = filter_date_value[
                    "selected_start_date"
                ]
                dashboard_rec.element_end_date = filter_date_value["selected_end_date"]

    @api.onchange("date_filter_selection_2")
    def date_filter_func_2(self):
        for dashboard_rec in self:
            if (
                not dashboard_rec.date_filter_selection_2
            ) or dashboard_rec.date_filter_selection_2 == "none":
                dashboard_rec.starting_date_kpi_2 = (
                    dashboard_rec.element_end_date
                ) = False
            elif dashboard_rec.date_filter_selection_2 != "last_custom":
                filter_date_value = generate_date(dashboard_rec.date_filter_selection_2)
                dashboard_rec.starting_date_kpi_2 = filter_date_value[
                    "selected_start_date"
                ]
                dashboard_rec.ending_date_kpi_2 = filter_date_value["selected_end_date"]

    # TODO : Removed _value
    @api.depends(
        "chart_data_calculation_field",
        "group_chart_relation",
        "chart_group_field",
        "domain",
        "type_of_element",
        "model_id",
        "sorting_selection_by_field",
        "sorting_selection",
        "filter_limit",
        "data_calculation_type_chart",
        "chart_data_calculation_field_2",
        "is_goal_enable",
        "goal_value_field",
        "goal_line_field",
        "chart_sub_field",
        "chart_sub_field_date",
        "date_filter_field",
        "element_start_date",
        "element_end_date",
        "time_of_comparation",
        "year_period",
        "unit",
        "unit_selection",
        "chart_unit",
    )
    def _compute_chart_data_func(self):
        for dashboard_rec in self:

            if (
                dashboard_rec.type_of_element
                and dashboard_rec.type_of_element != "tile"
                and dashboard_rec.type_of_element != "list_view"
                and dashboard_rec.model_id
                and dashboard_rec.data_calculation_type_chart
            ):
                chart_data = {
                    "labels": [],
                    "datasets": [],
                    "currency": 0,
                    "field": "",
                    "selection": "",
                    "show_second_y_scale": False,
                    "domains": [],
                }
                chart_data_calculation_field = []
                chart_data_calculation_field_2 = []
                chart_measure_field_2_ids = []

                if dashboard_rec.unit and dashboard_rec.unit_selection == "monetary":
                    chart_data["selection"] += dashboard_rec.unit_selection
                    chart_data[
                        "currency"
                    ] += dashboard_rec.env.user.company_id.currency_id.id
                elif dashboard_rec.unit and dashboard_rec.unit_selection == "custom":
                    chart_data["selection"] += dashboard_rec.unit_selection
                    if dashboard_rec.chart_unit:
                        chart_data["field"] += dashboard_rec.chart_unit

                if dashboard_rec.data_calculation_type_chart == "count":
                    chart_data["datasets"].append({"data": [], "label": "Count"})
                else:
                    if dashboard_rec.type_of_element == "bar_chart":
                        if dashboard_rec.chart_data_calculation_field_2:
                            chart_data["show_second_y_scale"] = True

                        for res in dashboard_rec.chart_data_calculation_field_2:
                            chart_data_calculation_field_2.append(res.name)
                            chart_measure_field_2_ids.append(res.id)
                            chart_data["datasets"].append(
                                {
                                    "data": [],
                                    "label": res.field_description,
                                    "type": "line",
                                    "yAxisID": "y-axis-1",
                                }
                            )

                    for res in dashboard_rec.chart_data_calculation_field:
                        chart_data_calculation_field.append(res.name)
                        chart_data["datasets"].append(
                            {"data": [], "label": res.field_description}
                        )

                chart_groupby_relation_field = dashboard_rec.group_chart_relation.name

                chart_domain = self.convert_into_proper_domain(
                    dashboard_rec.domain, dashboard_rec
                )
                chart_data["previous_domain"] = chart_domain
                orderby = (
                    dashboard_rec.sorting_selection_by_field.name
                    if dashboard_rec.sorting_selection_by_field
                    else "id"
                )
                if dashboard_rec.sorting_selection:
                    orderby = orderby + " " + dashboard_rec.sorting_selection
                limit = (
                    dashboard_rec.filter_limit
                    if dashboard_rec.filter_limit and dashboard_rec.filter_limit > 0
                    else False
                )

                if (
                    (
                        dashboard_rec.data_calculation_type_chart != "count"
                        and chart_data_calculation_field
                    )
                    or (
                        dashboard_rec.data_calculation_type_chart == "count"
                        and not chart_data_calculation_field
                    )
                ) and not dashboard_rec.chart_sub_field:
                    if (
                        dashboard_rec.group_chart_relation.ttype == "date"
                        and dashboard_rec.chart_group_field in ("minute", "hour")
                    ):
                        raise ValidationError(
                            _("Groupby field: {} cannot be aggregated by {}").format(
                                dashboard_rec.group_chart_relation.display_name,
                                dashboard_rec.chart_group_field,
                            )
                        )
                        chart_group_field = "day"
                    else:
                        chart_group_field = dashboard_rec.chart_group_field

                    if (
                        dashboard_rec.group_chart_field == "date_type"
                        and dashboard_rec.chart_group_field
                    ) or dashboard_rec.group_chart_field != "date_type":
                        chart_data = dashboard_rec.chart_data_sub_func(
                            dashboard_rec.model_name,
                            chart_domain,
                            chart_data_calculation_field,
                            chart_data_calculation_field_2,
                            chart_groupby_relation_field,
                            chart_group_field,
                            dashboard_rec.group_chart_field,
                            orderby,
                            limit,
                            dashboard_rec.data_calculation_type_chart,
                            dashboard_rec.chart_data_calculation_field.ids,
                            chart_measure_field_2_ids,
                            dashboard_rec.group_chart_relation.id,
                            chart_data,
                        )

                        if (
                            dashboard_rec.group_chart_field == "date_type"
                            and dashboard_rec.is_goal_enable
                            and dashboard_rec.type_of_element
                            in [
                                "bar_chart",
                                "horizontalBar_chart",
                                "line_chart",
                                "area_chart",
                            ]
                            and dashboard_rec.group_chart_field == "date_type"
                        ):

                            if dashboard_rec._context.get("current_id", False):
                                element_id = dashboard_rec._context["current_id"]
                            else:
                                element_id = dashboard_rec.id

                            if dashboard_rec.date_domain_fields == "none":
                                selected_start_date = dashboard_rec._context.get(
                                    "DateFilterStartDate", False
                                )
                                selected_end_date = dashboard_rec._context.get(
                                    "DateFilterEndDate", False
                                )

                            else:
                                if dashboard_rec.date_domain_fields == "last_custom":
                                    selected_start_date = (
                                        dashboard_rec.element_start_date
                                    )
                                    selected_end_date = dashboard_rec.element_start_date
                                else:
                                    filter_date_value = generate_date(
                                        dashboard_rec.date_domain_fields
                                    )
                                    selected_start_date = filter_date_value[
                                        "selected_start_date"
                                    ]
                                    selected_end_date = filter_date_value[
                                        "selected_end_date"
                                    ]

                            if selected_start_date and selected_end_date:
                                selected_start_date = selected_start_date.strftime(
                                    "%Y-%m-%d"
                                )
                                selected_end_date = selected_end_date.strftime(
                                    "%Y-%m-%d"
                                )
                            goal_domain = [("dashboard_element", "=", element_id)]

                            if selected_start_date and selected_end_date:
                                goal_domain.extend(
                                    [
                                        (
                                            "goal_date",
                                            ">=",
                                            selected_start_date.split(" ")[0],
                                        ),
                                        (
                                            "goal_date",
                                            "<=",
                                            selected_end_date.split(" ")[0],
                                        ),
                                    ]
                                )

                            filter_date_value = dashboard_rec.get_start_end_date(
                                dashboard_rec.model_name,
                                chart_groupby_relation_field,
                                dashboard_rec.group_chart_relation.ttype,
                                chart_domain,
                                goal_domain,
                            )

                            labels = []
                            if (
                                filter_date_value["start_date"]
                                and filter_date_value["end_date"]
                                and dashboard_rec.goal_lines
                            ):
                                labels = self.create_time_pattern_func(
                                    filter_date_value["start_date"],
                                    filter_date_value["end_date"],
                                    dashboard_rec.chart_group_field,
                                )

                            goal_records = self.env[
                                "dashboard_pro.element_target"
                            ].read_group(
                                goal_domain,
                                ["goal_value"],
                                ["goal_date" + ":" + chart_group_field],
                            )
                            goal_labels = []
                            goal_dataset = []
                            goal_dataset = []

                            if (
                                dashboard_rec.goal_lines
                                and len(dashboard_rec.goal_lines) != 0
                            ):
                                goal_domains = {}
                                for res in goal_records:
                                    if res["goal_date" + ":" + chart_group_field]:
                                        goal_labels.append(
                                            res["goal_date" + ":" + chart_group_field]
                                        )
                                        goal_dataset.append(res["goal_value"])
                                        goal_domains[
                                            res["goal_date" + ":" + chart_group_field]
                                        ] = res["__domain"]

                                for goal_domain in goal_domains.keys():
                                    goal_doamins = []
                                    for item in goal_domains[goal_domain]:

                                        if "goal_date" in item:
                                            domain = list(item)
                                            domain[0] = chart_groupby_relation_field
                                            domain = tuple(domain)
                                            goal_doamins.append(domain)
                                    goal_doamins.insert(0, "&")
                                    goal_domains[goal_domain] = goal_doamins

                                domains = {}
                                counter = 0
                                for label in chart_data["labels"]:
                                    domains[label] = chart_data["domains"][counter]
                                    counter += 1

                                chart_records_dates = chart_data["labels"] + list(
                                    set(goal_labels) - set(chart_data["labels"])
                                )

                                chart_records = []
                                for label in labels:
                                    if label in chart_records_dates:
                                        chart_records.append(label)

                                chart_data["domains"].clear()
                                datasets = []
                                for dataset in chart_data["datasets"]:
                                    datasets.append(dataset["data"].copy())

                                for dataset in chart_data["datasets"]:
                                    dataset["data"].clear()

                                for label in chart_records:
                                    domain = domains.get(label, False)
                                    if domain:
                                        chart_data["domains"].append(domain)
                                    else:
                                        chart_data["domains"].append(
                                            goal_domains.get(label, [])
                                        )
                                    counterr = 0
                                    if label in chart_data["labels"]:
                                        index = chart_data["labels"].index(label)

                                        for dataset in chart_data["datasets"]:
                                            dataset["data"].append(
                                                datasets[counterr][index]
                                            )
                                            counterr += 1

                                    else:
                                        for dataset in chart_data["datasets"]:
                                            dataset["data"].append(0.00)

                                    if label in goal_labels:
                                        index = goal_labels.index(label)
                                        goal_dataset.append(goal_dataset[index])
                                    else:
                                        goal_dataset.append(0.00)

                                chart_data["labels"] = chart_records
                            else:
                                if dashboard_rec.goal_value_field:
                                    length_all = len(chart_data["datasets"][0]["data"])
                                    for i in range(length_all): # noqa
                                        goal_dataset.append(
                                            dashboard_rec.goal_value_field
                                        )
                            goal_datasets = {
                                "label": "Target",
                                "data": goal_dataset,
                            }
                            if (
                                dashboard_rec.goal_line_field
                                and dashboard_rec.type_of_element == "bar_chart"
                            ):
                                goal_datasets["type"] = "line"
                                chart_data["datasets"].insert(0, goal_datasets)
                            else:
                                chart_data["datasets"].append(goal_datasets)

                elif dashboard_rec.chart_sub_field and (
                    (dashboard_rec.sub_group_chart_field == "relational_type")
                    or (dashboard_rec.sub_group_chart_field == "selection")
                    or (
                        dashboard_rec.sub_group_chart_field == "date_type"
                        and dashboard_rec.chart_sub_field_date
                    )
                    or (dashboard_rec.sub_group_chart_field == "other")
                ):
                    if dashboard_rec.chart_sub_field.ttype == "date":
                        if dashboard_rec.chart_sub_field_date in ("minute", "hour"):
                            raise ValidationError(
                                _(
                                    "Sub Groupby field: {} cannot be aggregated by {}"
                                ).format(
                                    dashboard_rec.chart_sub_field.display_name,
                                    dashboard_rec.chart_sub_field_date,
                                )
                            )
                        if dashboard_rec.chart_group_field in ("minute", "hour"):
                            raise ValidationError(
                                _(
                                    "Groupby field: {} cannot be aggregated by {}"
                                ).format(
                                    dashboard_rec.chart_sub_field.display_name,
                                    dashboard_rec.chart_group_field,
                                )
                            )
                        chart_sub_field_date = dashboard_rec.chart_sub_field_date
                        chart_group_field = dashboard_rec.chart_group_field
                    else:
                        chart_sub_field_date = dashboard_rec.chart_sub_field_date
                        chart_group_field = dashboard_rec.chart_group_field
                    if (
                        len(chart_data_calculation_field) != 0
                        or dashboard_rec.data_calculation_type_chart == "count"
                    ):
                        if (
                            dashboard_rec.group_chart_field == "date_type"
                            and chart_group_field
                        ):
                            chart_group = (
                                dashboard_rec.group_chart_relation.name
                                + ":"
                                + chart_group_field
                            )
                        else:
                            chart_group = dashboard_rec.group_chart_relation.name

                        if (
                            dashboard_rec.sub_group_chart_field == "date_type"
                            and dashboard_rec.chart_sub_field_date
                        ):
                            chart_sub_groupby_field = (
                                dashboard_rec.chart_sub_field.name
                                + ":"
                                + chart_sub_field_date
                            )
                        else:
                            chart_sub_groupby_field = dashboard_rec.chart_sub_field.name

                        chart_groupby_relation_fields = [
                            chart_group,
                            chart_sub_groupby_field,
                        ]
                        chart_record = self.env[dashboard_rec.model_name].read_group(
                            chart_domain,
                            set(
                                chart_data_calculation_field
                                + chart_data_calculation_field_2
                                + [
                                    chart_groupby_relation_field,
                                    dashboard_rec.chart_sub_field.name,
                                ]
                            ),
                            chart_groupby_relation_fields,
                            orderby=orderby,
                            limit=limit,
                            lazy=False,
                        )
                        chart_data = []
                        chart_sub_data = []
                        for res in chart_record:
                            domain = res.get("__domain", [])
                            if (
                                res[chart_groupby_relation_fields[0]]
                                and res[chart_groupby_relation_fields[1]]
                            ):
                                if dashboard_rec.group_chart_field == "date_type":
                                    if (
                                        dashboard_rec.chart_group_field == "day"
                                        and dashboard_rec.chart_sub_field_date
                                        in ["quarter", "year"]
                                    ):
                                        label = " ".join(
                                            res[chart_groupby_relation_fields[0]].split(
                                                " "
                                            )[:-1]
                                        )
                                    elif (
                                        dashboard_rec.chart_group_field == "day"
                                        and dashboard_rec.chart_sub_field_date
                                        not in ["quarter", "year"]
                                    ):
                                        label = res[
                                            chart_groupby_relation_fields[0]
                                        ].split(" ")[0]
                                    elif dashboard_rec.chart_group_field in [
                                        "minute",
                                        "hour",
                                    ] and dashboard_rec.chart_sub_field_date in [
                                        "month",
                                        "week",
                                        "quarter",
                                        "year",
                                    ]:
                                        label = " ".join(
                                            res[chart_groupby_relation_fields[0]].split(
                                                " "
                                            )[:]
                                        )
                                    elif dashboard_rec.chart_group_field in [
                                        "minute",
                                        "hour",
                                    ] and dashboard_rec.chart_sub_field_date in [
                                        "minute",
                                        "hour",
                                        "day",
                                    ]:
                                        label = res[
                                            chart_groupby_relation_fields[0]
                                        ].split(" ")[0]
                                    else:
                                        label = " ".join(
                                            res[chart_groupby_relation_fields[0]].split(
                                                " "
                                            )[:-1]
                                        )
                                elif dashboard_rec.group_chart_field == "selection":
                                    selection = res[chart_groupby_relation_fields[0]]
                                    label = dict(
                                        self.env[dashboard_rec.model_name].fields_get(
                                            allfields=[chart_groupby_relation_fields[0]]
                                        )[chart_groupby_relation_fields[0]]["selection"]
                                    )[selection]
                                elif (
                                    dashboard_rec.group_chart_field == "relational_type"
                                ):
                                    label = res[chart_groupby_relation_fields[0]][
                                        1
                                    ]._value
                                elif dashboard_rec.group_chart_field == "other":
                                    label = res[chart_groupby_relation_fields[0]]

                                labels = []
                                value = []
                                value_2 = []
                                labels_2 = []
                                if dashboard_rec.data_calculation_type_chart != "count":
                                    for (
                                        ress
                                    ) in dashboard_rec.chart_data_calculation_field:
                                        if (
                                            dashboard_rec.sub_group_chart_field
                                            == "date_type"
                                        ):
                                            labels.append(
                                                res[
                                                    chart_groupby_relation_fields[1]
                                                ].split(" ")[0]
                                                + " "
                                                + ress.field_description
                                            )
                                        elif (
                                            dashboard_rec.sub_group_chart_field
                                            == "selection"
                                        ):
                                            selection = res[
                                                chart_groupby_relation_fields[1]
                                            ]
                                            labels.append(
                                                dict(
                                                    self.env[
                                                        dashboard_rec.model_name
                                                    ].fields_get(
                                                        allfields=[
                                                            chart_groupby_relation_fields[ # noqa
                                                                1
                                                            ]
                                                        ]
                                                    )[
                                                        chart_groupby_relation_fields[1]
                                                    ][
                                                        "selection"
                                                    ]
                                                )[selection]
                                                + " "
                                                + ress.field_description
                                            )
                                        elif (
                                            dashboard_rec.sub_group_chart_field
                                            == "relational_type"
                                        ):
                                            labels.append(
                                                res[chart_groupby_relation_fields[1]][
                                                    1
                                                ]._value
                                                + " "
                                                + ress.field_description
                                            )
                                        elif (
                                            dashboard_rec.sub_group_chart_field
                                            == "other"
                                        ):
                                            labels.append(
                                                str(
                                                    res[
                                                        chart_groupby_relation_fields[1]
                                                    ]
                                                )
                                                + "'s "
                                                + ress.field_description
                                            )

                                        value.append(
                                            res.get(ress.name)
                                            if dashboard_rec.data_calculation_type_chart
                                            == "sum"
                                            else res.get(ress.name) / res.get("__count")
                                        )

                                    if (
                                        dashboard_rec.chart_data_calculation_field_2
                                        and dashboard_rec.type_of_element == "bar_chart"
                                    ):
                                        for (
                                            ress
                                        ) in (
                                            dashboard_rec.chart_data_calculation_field_2
                                        ):
                                            if (
                                                dashboard_rec.sub_group_chart_field
                                                == "date_type"
                                            ):
                                                labels_2.append(
                                                    res[
                                                        chart_groupby_relation_fields[1]
                                                    ].split(" ")[0]
                                                    + " "
                                                    + ress.field_description
                                                )
                                            elif (
                                                dashboard_rec.sub_group_chart_field
                                                == "selection"
                                            ):
                                                selection = res[
                                                    chart_groupby_relation_fields[1]
                                                ]
                                                labels_2.append(
                                                    dict(
                                                        self.env[
                                                            dashboard_rec.model_name
                                                        ].fields_get(
                                                            allfields=[
                                                                chart_groupby_relation_fields[ # noqa
                                                                    1
                                                                ]
                                                            ]
                                                        )[
                                                            chart_groupby_relation_fields[ # noqa
                                                                1
                                                            ]
                                                        ][
                                                            "selection"
                                                        ]
                                                    )[selection]
                                                    + " "
                                                    + ress.field_description
                                                )
                                            elif (
                                                dashboard_rec.sub_group_chart_field
                                                == "relational_type"
                                            ):
                                                labels_2.append(
                                                    res[
                                                        chart_groupby_relation_fields[1]
                                                    ][1]._value
                                                    + " "
                                                    + ress.field_description
                                                )
                                            elif (
                                                dashboard_rec.sub_group_chart_field
                                                == "other"
                                            ):
                                                labels_2.append(
                                                    str(
                                                        res[
                                                            chart_groupby_relation_fields[ # noqa
                                                                1
                                                            ]
                                                        ]
                                                    )
                                                    + " "
                                                    + ress.field_description
                                                )

                                            value_2.append(
                                                res.get(ress.name)
                                                if dashboard_rec.data_calculation_type_chart # noqa
                                                == "sum"
                                                else res.get(ress.name)
                                                / res.get("__count")
                                            )

                                        chart_sub_data.append(
                                            {
                                                "value": value_2,
                                                "labels": label,
                                                "series": labels_2,
                                                "domain": domain,
                                            }
                                        )
                                else:
                                    if (
                                        dashboard_rec.sub_group_chart_field
                                        == "date_type"
                                    ):
                                        labels.append(
                                            res[chart_groupby_relation_fields[1]].split(
                                                " "
                                            )[0]
                                        )
                                    elif (
                                        dashboard_rec.sub_group_chart_field
                                        == "selection"
                                    ):
                                        selection = res[
                                            chart_groupby_relation_fields[1]
                                        ]
                                        labels.append(
                                            dict(
                                                self.env[
                                                    dashboard_rec.model_name
                                                ].fields_get(
                                                    allfields=[
                                                        chart_groupby_relation_fields[1]
                                                    ]
                                                )[
                                                    chart_groupby_relation_fields[1]
                                                ][
                                                    "selection"
                                                ]
                                            )[selection]
                                        )
                                    elif (
                                        dashboard_rec.sub_group_chart_field
                                        == "relational_type"
                                    ):
                                        labels.append(
                                            res[chart_groupby_relation_fields[1]][
                                                1
                                            ]._value
                                        )
                                    elif dashboard_rec.sub_group_chart_field == "other":
                                        labels.append(
                                            res[chart_groupby_relation_fields[1]]
                                        )
                                    value.append(res["__count"])

                                chart_data.append(
                                    {
                                        "value": value,
                                        "labels": label,
                                        "series": labels,
                                        "domain": domain,
                                    }
                                )

                        xlabels = []
                        series = []
                        values = {}
                        domains = {}
                        for data in chart_data:
                            label = data["labels"]
                            serie = data["series"]
                            domain = data["domain"]

                            if (len(xlabels) == 0) or (label not in xlabels):
                                xlabels.append(label)

                            if label not in domains:
                                domains[label] = domain
                            else:
                                domains[label].insert(0, "|")
                                domains[label] = domains[label] + domain

                            series = series + serie
                            value = data["value"]
                            counter = 0
                            for seri in serie:
                                if seri not in values:
                                    values[seri] = {}
                                if label in values[seri]:
                                    values[seri][label] = (
                                        values[seri][label] + value[counter]
                                    )
                                else:
                                    values[seri][label] = value[counter]
                                counter += 1

                        final_datasets = []
                        for serie in series:
                            if serie not in final_datasets:
                                final_datasets.append(serie)

                        data = []
                        for dataset in final_datasets:
                            pro_dataset = {"value": [], "key": dataset}
                            for label in xlabels:
                                pro_dataset["value"].append(
                                    {
                                        "domain": domains[label],
                                        "x": label,
                                        "y": values[dataset][label]
                                        if label in values[dataset]
                                        else 0,
                                    }
                                )
                            data.append(pro_dataset)

                        if (
                            dashboard_rec.chart_sub_field.name
                            == dashboard_rec.group_chart_relation.name
                            == dashboard_rec.sorting_selection_by_field.name
                        ):
                            data = dashboard_rec.gropu_data_sort_func(
                                data,
                                dashboard_rec.group_chart_field,
                                dashboard_rec.chart_group_field,
                                dashboard_rec.sorting_selection,
                                dashboard_rec.chart_sub_field_date,
                            )

                        chart_data = {
                            "labels": [],
                            "datasets": [],
                            "domains": [],
                            "selection": "",
                            "currency": 0,
                            "field": "",
                        }

                        if (
                            dashboard_rec.unit
                            and dashboard_rec.unit_selection == "monetary"
                        ):
                            chart_data["selection"] += dashboard_rec.unit_selection
                            chart_data[
                                "currency"
                            ] += dashboard_rec.env.user.company_id.currency_id.id
                        elif (
                            dashboard_rec.unit
                            and dashboard_rec.unit_selection == "custom"
                        ):
                            chart_data["selection"] += dashboard_rec.unit_selection
                            if dashboard_rec.chart_unit:
                                chart_data["field"] += dashboard_rec.chart_unit

                        if len(data) != 0:
                            for res in data[0]["value"]:
                                chart_data["labels"].append(res["x"])
                                chart_data["domains"].append(res["domain"])
                            if (
                                dashboard_rec.chart_data_calculation_field_2
                                and dashboard_rec.type_of_element == "bar_chart"
                            ):
                                chart_data["show_second_y_scale"] = True
                                values_2 = {}
                                series_2 = []
                                for data in chart_sub_data:
                                    label = data["labels"]
                                    serie = data["series"]
                                    series_2 = series_2 + serie
                                    value = data["value"]

                                    counter = 0
                                    for seri in serie:
                                        if seri not in values_2:
                                            values_2[seri] = {}
                                        if label in values_2[seri]:
                                            values_2[seri][label] = (
                                                values_2[seri][label] + value[counter]
                                            )
                                        else:
                                            values_2[seri][label] = value[counter]
                                        counter += 1
                                final_datasets_2 = []
                                for serie in series_2:
                                    if serie not in final_datasets_2:
                                        final_datasets_2.append(serie)
                                data_2 = []
                                for dataset in final_datasets_2:
                                    pro_dataset = {"value": [], "key": dataset}
                                    for label in xlabels:
                                        pro_dataset["value"].append(
                                            {
                                                "x": label,
                                                "y": values_2[dataset][label]
                                                if label in values_2[dataset]
                                                else 0,
                                            }
                                        )
                                    data_2.append(pro_dataset)

                                for dat in data_2:
                                    dataset = {
                                        "label": dat["key"],
                                        "data": [],
                                        "type": "line",
                                        "yAxisID": "y-axis-1",
                                    }
                                    for res in dat["value"]:
                                        dataset["data"].append(res["y"])

                                    chart_data["datasets"].append(dataset)
                            for dat in data:
                                dataset = {"label": dat["key"], "data": []}
                                for res in dat["value"]:
                                    dataset["data"].append(res["y"])

                                chart_data["datasets"].append(dataset)

                            if (
                                dashboard_rec.is_goal_enable
                                and dashboard_rec.goal_value_field
                                and dashboard_rec.type_of_element
                                in [
                                    "bar_chart",
                                    "line_chart",
                                    "area_chart",
                                    "horizontalBar_chart",
                                ]
                            ):
                                goal_dataset = []
                                length_all = len(chart_data["datasets"][0]["data"])
                                for i in range(length_all): # noqa
                                    goal_dataset.append(dashboard_rec.goal_value_field)
                                goal_datasets = {
                                    "label": "Target",
                                    "data": goal_dataset,
                                }
                                if (
                                    dashboard_rec.goal_line_field
                                    and dashboard_rec.type_of_element
                                    != "horizontalBar_chart"
                                ):
                                    goal_datasets["type"] = "line"
                                    chart_data["datasets"].insert(0, goal_datasets)
                                else:
                                    chart_data["datasets"].append(goal_datasets)
                    else:
                        chart_data = False

                dashboard_rec.chart_data = json.dumps(chart_data)
            else:
                dashboard_rec.chart_data = False

    @api.model
    def get_start_end_date(
        self, model_name, chart_groupby_relation_field, ttype, chart_domain, goal_domain
    ):
        start_end_date = {}
        try:
            model_field_start_date = self.env[model_name].search(
                chart_domain + [(chart_groupby_relation_field, "!=", False)],
                limit=1,
                order=chart_groupby_relation_field + " ASC",
            )[chart_groupby_relation_field]
            model_field_end_date = self.env[model_name].search(
                chart_domain + [(chart_groupby_relation_field, "!=", False)],
                limit=1,
                order=chart_groupby_relation_field + " DESC",
            )[chart_groupby_relation_field]
        except Exception:
            model_field_start_date = model_field_end_date = False

        goal_model_start_date = self.env["dashboard_pro.element_target"].search(
            goal_domain, limit=1, order="goal_date ASC"
        )["goal_date"]
        goal_model_end_date = self.env["dashboard_pro.element_target"].search(
            goal_domain, limit=1, order="goal_date DESC"
        )["goal_date"]

        if model_field_start_date and ttype == "date":
            model_field_end_date = datetime.combine(
                model_field_end_date, datetime.min.time()
            )
            model_field_start_date = datetime.combine(
                model_field_start_date, datetime.min.time()
            )

        if model_field_start_date and goal_model_start_date:
            goal_model_start_date = datetime.combine(
                goal_model_start_date, datetime.min.time()
            )
            goal_model_end_date = datetime.combine(
                goal_model_end_date, datetime.max.time()
            )
            if model_field_start_date < goal_model_start_date:
                start_end_date["start_date"] = model_field_start_date.strftime(
                    "%Y-%m-%d 00:00:00"
                )
            else:
                start_end_date["start_date"] = goal_model_start_date.strftime(
                    "%Y-%m-%d 00:00:00"
                )
            if model_field_end_date > goal_model_end_date:
                start_end_date["end_date"] = model_field_end_date.strftime(
                    "%Y-%m-%d 23:59:59"
                )
            else:
                start_end_date["end_date"] = goal_model_end_date.strftime(
                    "%Y-%m-%d 23:59:59"
                )

        elif model_field_start_date and not goal_model_start_date:
            start_end_date["start_date"] = model_field_start_date.strftime(
                "%Y-%m-%d 00:00:00"
            )
            start_end_date["end_date"] = model_field_end_date.strftime(
                "%Y-%m-%d 23:59:59"
            )

        elif goal_model_start_date and not model_field_start_date:
            start_end_date["start_date"] = goal_model_start_date.strftime(
                "%Y-%m-%d 00:00:00"
            )
            start_end_date["end_date"] = goal_model_start_date.strftime(
                "%Y-%m-%d 23:59:59"
            )
        else:
            start_end_date["start_date"] = False
            start_end_date["end_date"] = False

        return start_end_date

    @api.model
    def next_offset_func(self, element_id, offset):
        record = self.browse(element_id)
        offset = int(offset["offset"])
        json_list_data = self.list_info_sub_func(record, offset=int(offset))

        return {
            "json_list_data": json.dumps(json_list_data),
            "offset": int(offset) + 1,
            "next_offset": int(offset) + len(json_list_data["data_rows"]),
            "limit": record.filter_limit if record.filter_limit else 0,
        }


class DashboardProElementTarget(models.Model):
    _name = "dashboard_pro.element_target"
    _description = "Dashboard Element Target Object And Model."

    goal_date = fields.Date(string="Date")
    goal_value = fields.Float(string="Value")

    dashboard_element = fields.Many2one(
        "dashboard_pro.element", string="Dashboard Item"
    )


class DashboardElementAction(models.Model):
    _name = "dashboard_pro.element_action"
    _description = "Dashboard Element Action Model"

    item_action_field = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',model_id),('name','!=','id'),('store','=',True),"
        "('ttype','!=','binary'),('ttype','!=','many2many'), "
        "('ttype','!=','one2many')]",
        string="Action Group By",
    )

    item_action_field_type = fields.Char(
        compute="_compute_get_item_action_type", compute_sudo=False
    )

    item_action_date_groupby = fields.Selection(
        [
            ("minute", "Minute"),
            ("hour", "Hour"),
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        string="Group By Date",
    )

    chart_type = fields.Selection(
        [
            ("bar_chart", "Bar Chart"),
            ("horizontalBar_chart", "Horizontal Bar Chart"),
            ("line_chart", "Line Chart"),
            ("area_chart", "Area Chart"),
            ("pie_chart", "Pie Chart"),
            ("doughnut_chart", "Doughnut Chart"),
            ("polarArea_chart", "Polar Area Chart"),
            ("list_view", "List View"),
        ],
        string="Item Type",
    )

    dashboard_item_id = fields.Many2one(
        "dashboard_pro.element", string="Dashboard Item"
    )
    model_id = fields.Many2one("ir.model", related="dashboard_item_id.model_id")
    sequence = fields.Integer(string="Sequence")
    record_limit = fields.Integer(string="Record Limit")
    sorting_selection_by_field = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=',model_id),('name','!=','id'),('store','=',True),"
        "('ttype','!=','one2many'),('ttype','!=','many2one'),"
        "('ttype','!=','binary')]",
        string="Sort By Field",
    )
    sorting_selection = fields.Selection(
        [("ASC", "Ascending"), ("DESC", "Descending")], string="Sort Order"
    )

    @api.depends("item_action_field")
    def _compute_get_item_action_type(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.item_action_field.ttype == "datetime"
                or dashboard_rec.item_action_field.ttype == "date"
            ):
                dashboard_rec.item_action_field_type = "date_type"
            elif dashboard_rec.item_action_field.ttype == "many2one":
                dashboard_rec.item_action_field_type = "relational_type"
            elif dashboard_rec.item_action_field.ttype == "selection":
                dashboard_rec.item_action_field_type = "selection"

            else:
                dashboard_rec.item_action_field_type = "none"

    @api.onchange("item_action_date_groupby")
    def check_date_group_by(self):
        for dashboard_rec in self:
            if (
                dashboard_rec.item_action_field.ttype == "date"
                and dashboard_rec.item_action_date_groupby in ["hour", "minute"]
            ):
                raise ValidationError(
                    _("Action field: {} cannot be aggregated by {}").format(
                        dashboard_rec.item_action_field.display_name,
                        dashboard_rec.item_action_date_groupby,
                    )
                )
