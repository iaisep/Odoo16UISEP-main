odoo.define('openeducat_dashboard_kpi.dashboard_pro', function(require) {
    "use strict";

    var session = require('web.session');
    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var Dialog = require('web.Dialog');
    var viewRegistry = require('web.view_registry');
    var _t = core._t;
    var QWeb = core.qweb;
    var utils = require('web.utils');
    var config = require('web.config');
    var framework = require('web.framework');
    var time = require('web.time');
    var datepicker = require("web.datepicker");
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var framework = require('web.framework');
    var field_utils = require('web.field_utils');
    var GlobalFunction = require('openeducat_dashboard_kpi.FormattingFunction');

    var DashboardPro = AbstractAction.extend({
        hasControlPanel: false,
        events: {
            'click .full_screen_element': '_onClickFullScreenMode',
            'click .close_full_screen': '_onClickCloseFullScreen',
            'click .add_element_submenu_menu > li': 'AddElementDashboard',
            'click #dashboard_theme_selection > li': 'DashboardThemeSelection',
            'click .dashboard_add_layout': '_onAddLayoutClick',
            'click .dashboard_edit_layout': '_onEditLayoutClick',
            'click .dashboard_select_item': 'onSelectItemClick',
            'click .dashboard_save_layout': '_onSaveLayoutClick',
            'click .dashboard_cancel_layout': 'CancelLayout',
            'click .element_click': 'ElementClick',
            'click .load_previous': 'LoadPreviousRecords',
            'click .theme_toggle_button':'_ChangeDashBoardTheme',
            'click .load_next': 'LoadMoreRecords',
            'click #dashboard_layout_refresh' : 'OnRefreshButton',
            'click .dashboard_element_edit': 'ElementCustomization',
            'click .dashboard_element_delete': 'DeleteElement',
            'change .dashboard_header_name': '_onInputChange',
            'click .duplicate_item': 'DuplicateElement',
            'click .move_item': 'MoveElement',
            'change .input_import_item_button': 'importElement',
            'click .dashboard_menu_container': function(e) {
                e.stopPropagation();
            },
            'click .qe_dropdown_menu': function(e) {
                e.stopPropagation();
            },
            'click .chart_json_export': 'ItemExportJson',
            'click .dashboard_item_action': 'StopClickPropagation',
            'show.bs.dropdown .dropdown_container': 'onDashboardMenuContainerShow',
            'hide.bs.dropdown .dashboard_element_buttons_container': 'onDashboardMenuContainerHide',
            'click .apply-dashboard-date-filter': '_onApplyDateFilter',
            'click .clear-dashboard-date-filter': '_onClearDateValues',
            'click .apply-specific-dashboard-date-filter': '_onApplySpecificDateFilter',
            'click .clear-specific-dashboard-date-filter': '_onClearDateValues',
            'change #start_date_picker': '_ShowApplyClearDateButton',
            'change #end_date_picker': '_ShowApplyClearDateButton',
            'change #start_specific_date_picker': '_ShowApplyClearDateButton',
            'change #end_specific_date_picker': '_ShowApplyClearDateButton',
            'click .date_filters_menu': '_OnDateFilterMenuSelect',
            'click .date_specific_filters_menu': '_OnDateSpecificFilterMenuSelect',
            'click #item_info': 'ListElementClick',
            'click .chart_color_options': 'ChartColorOptionsRender',
            'click #chart_canvas_id': 'onChartCanvasClick',
            'click .list_canvas_click': 'onChartCanvasClick',
            'click #delete_todo_list' : 'DeleteToDoList',
            'click .change_to_do_done_state_text': 'ChangeToDoState',
            'click .dashboard_item_chart_info': 'onChartMoreInfoClick',
            'click .chart_xls_csv_export': 'ChartExportXlsCsv',
            'click .chart_pdf_export': 'ChartExportPdf',

        },
        jsLibs: ['/openeducat_dashboard_kpi/static/lib/js/jquery.ui.touch-punch.min.js',
            '/openeducat_dashboard_kpi/static/lib/js/jsPDF.js',
            '/openeducat_dashboard_kpi/static/lib/js/Chart.bundle.min.js',
            '/openeducat_dashboard_kpi/static/lib/js/gridstack.min.js',
            '/openeducat_dashboard_kpi/static/lib/js/gridstack.jQueryUI.min.js',
            '/openeducat_dashboard_kpi/static/lib/js/chartjs-plugin-datalabels.js',
        ],
        cssLibs: ['/openeducat_dashboard_kpi/static/lib/css/Chart.css',
            '/openeducat_dashboard_kpi/static/lib/css/Chart.min.css'
        ],

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.action_manager = parent;
            this.controllerID = params.controllerID;
            this.name = "openeducat_dashboard_kpi";
            this.IsDashboardManager = false;
            this.DashboardEditMode = false;
            this.NewDashboardName = false;
            this.file_type_word = {
                '/': 'jpg',
                'R': 'gif',
                'i': 'png',
                'P': 'svg+xml',
            };
            this.AllowItemClick = true;

            var l10n = _t.database.parameters;
            this.form_template = 'dashboard_pro_template_view';
            this.date_format = time.strftime_to_moment_format(_t.database.parameters.date_format)
            this.date_format = this.date_format.replace(/\bYY\b/g, "YYYY");
            this.datetime_format = time.strftime_to_moment_format((_t.database.parameters.date_format + ' ' + l10n.time_format))
            this.date_filter_data;

            this.date_filter_selections = {
                'none': _t('Date Filter'),
                'last_day': _t('Today'),
                'this_week': _t('This Week'),
                'this_month': _t('This Month'),
                'this_quarter': _t('This Quarter'),
                'this_year': _t('This Year'),
                'next_day': _t('Next Day'),
                'next_week': _t('Next Week'),
                'next_month': _t('Next Month'),
                'next_quarter': _t('Next Quarter'),
                'next_year': _t('Next Year'),
                'lastp_day': _t('Last Day'),
                'lastp_week': _t('Last Week'),
                'lastp_month': _t('Last Month'),
                'lastp_quarter': _t('Last Quarter'),
                'lastp_year': _t('Last Year'),
                'last_week': _t('Last 7 days'),
                'last_month': _t('Last 30 days'),
                'last_quarter': _t('Last 90 days'),
                'last_year': _t('Last 365 days'),
                'last_custom': _t('Custom Filter'),
            };
            this.fullScreenOverlay = false;
            this.dashboard_id = state.params.dashboard_id;
            this.gridstack_options = {
                staticGrid: true,
                float: false,
                animate: true,
            };
            this.gridstackConfig = {};
            this.grid = false;
            this.chartMeasure = {};
            this.chart_container = {};
            this.list_container = {};
            this.ChartColorOptions = ['default', 'cool', 'warm', 'neon'];
            this.DashboardElementUpdate = this.DashboardElementUpdate.bind(this);
            this.dashboard_theme = 'light';
            this.DateFilterSelection = false;
            this.dashboard_theme_primary_color = false;
            this.dashboard_theme_secondary_color = false;
            this.dashboard_theme_font_color = false;
            this.DateFilterStartDate = false;
            this.DateFilterEndDate = false;
            this.UpdateDashboard = {};
            this.date_filter_selection_order = ['last_day', 'this_week', 'this_month', 'this_quarter', 'this_year', 'next_day',
                'next_week', 'next_month', 'next_quarter', 'next_year', 'lastp_day', 'lastp_week', 'lastp_month', 'lastp_quarter',
                'lastp_year', 'last_week', 'last_month', 'last_quarter', 'last_year', 'last_custom'
            ];
            this.date_specific_filter_selections = {
                'none': _t('Date Filter'),
                'last_day': _t('Today'),
                'this_week': _t('This Week'),
                'this_month': _t('This Month'),
                'this_quarter': _t('This Quarter'),
                'this_year': _t('This Year'),
                'next_day': _t('Next Day'),
                'next_week': _t('Next Week'),
                'next_month': _t('Next Month'),
                'next_quarter': _t('Next Quarter'),
                'next_year': _t('Next Year'),
                'lastp_day': _t('Last Day'),
                'lastp_week': _t('Last Week'),
                'lastp_month': _t('Last Month'),
                'lastp_quarter': _t('Last Quarter'),
                'lastp_year': _t('Last Year'),
                'last_week': _t('Last 7 days'),
                'last_month': _t('Last 30 days'),
                'last_quarter': _t('Last 90 days'),
                'last_year': _t('Last 365 days'),
            };
            this.date_specific_filter_selection_order = ['last_day', 'this_week', 'this_month', 'this_quarter', 'this_year', 'next_day',
                'next_week', 'next_month', 'next_quarter', 'next_year', 'lastp_day', 'lastp_week', 'lastp_month', 'lastp_quarter',
                'lastp_year', 'last_week', 'last_month', 'last_quarter', 'last_year'
            ];
        },

        getContext: function() {
            var self = this;
            var context = {
                DateFilterSelection: self.DateFilterSelection,
                DateFilterStartDate: self.DateFilterStartDate,
                DateFilterEndDate: self.DateFilterEndDate,
            }
            return Object.assign(context, session.user_context)
        },
        on_attach_callback: function() {
            var self = this;
            self.MainDashboardRender();
            self.update_time_diff();
            if (self.dashboard_data.element_data) {
                self.SaveLayout();
            }
        },
        update_time_diff: function() {
            var self = this;
            if (self.dashboard_data.element_data) {
                Object.keys(self.dashboard_data.element_data).forEach(function(element_id) {
                    var element_data = self.dashboard_data.element_data[element_id]
                    var updateValue = element_data["update_element_data_time"];
                    if (updateValue) {
                        if (!(element_id in self.UpdateDashboard)) {
                            if (['tile', 'list_view', 'kpi'].indexOf(element_data['type_of_element']) >= 0) {
                                var ItemUpdateInterval = setInterval(function() {
                                    self.GetUpdateElement(element_id)
                                }, updateValue);
                            } else {
                                var ItemUpdateInterval = setInterval(function() {
                                    self.ChartElementGet(element_id)
                                }, updateValue);
                            }
                            self.UpdateDashboard[element_id] = ItemUpdateInterval;
                        }
                    }
                });
            }
        },
        on_detach_callback: function() {
            var self = this;
            self.remove_time_diff();
            if (self.DashboardEditMode) self.SaveLayout();

            self.DateFilterSelection = false;
            self.DateFilterStartDate = false;
            self.DateFilterEndDate = false;
            self.fetch_data();
        },
        remove_time_diff: function() {
            var self = this;
            if (self.UpdateDashboard) {
                Object.values(self.UpdateDashboard).forEach(function(itemInterval) {
                    clearInterval(itemInterval);
                });
                self.UpdateDashboard = {};
            }
        },
        willStart: function() {
            var self = this;
            return $.when( this._super()).then(function() {
                return self.fetch_data();
            });
        },

        start: function() {
            var self = this;
            self.default_chart_view();
            return this._super();
        },
        ListElementClick: function(e) {
            var self = this;
            var element_id = e.currentTarget.dataset.itemId;
            var element_data = self.dashboard_data.element_data[element_id];
            var action = {
                name: element_data ? _t(element_data.name): false,
                type: 'ir.actions.act_window',
                res_model: e.currentTarget.dataset.model,
                domain: element_data ? element_data.domain : [] || [],
                views: [
                    [false, 'list'],
                    [false, 'form']
                ],
                target: 'current',
            }
            if (e.currentTarget.dataset.listViewType === "ungrouped") {
                action['view_mode'] = 'form';
                action['views'] = [
                    [false, 'form']
                ];
                action['res_id'] = parseInt(e.currentTarget.dataset.recordId);
            } else {
                if (e.currentTarget.dataset.listType === "date_type") {
                    var domain = JSON.parse(e.currentTarget.parentElement.parentElement.dataset.domain);
                    action['view_mode'] = 'list';
                    action['context'] = {
                        'group_by': e.currentTarget.dataset.groupby,
                    };
                    action['domain'] = domain;
                } else if (e.currentTarget.dataset.listType === "relational_type") {
                    var domain = JSON.parse(e.currentTarget.parentElement.parentElement.dataset.domain);
                    action['view_mode'] = 'list';
                    action['context'] = {
                        'group_by': e.currentTarget.dataset.groupby,
                    };
                    action['domain'] = domain;
                    action['context']['search_default_' + e.currentTarget.dataset.groupby] = parseInt(e.currentTarget.dataset.recordId);
                } else if (e.currentTarget.dataset.listType === "other") {
                    var domain = JSON.parse(e.currentTarget.parentElement.parentElement.dataset.domain);
                    action['view_mode'] = 'list';
                    action['context'] = {
                        'group_by': e.currentTarget.dataset.groupby,
                    };
                    action['context']['search_default_' + e.currentTarget.dataset.groupby] = parseInt(e.currentTarget.dataset.recordId);
                    action['domain'] = domain;
                }
            }
            self.do_action(action, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });
        },
        default_chart_view: function() {
            Chart.plugins.unregister(ChartDataLabels);
            Chart.plugins.register({
                beforeDraw: function(c) {
                    var ctx = c.chart.ctx;
                    ctx.fillStyle = "white";
                    ctx.fillRect(0, 0, c.chart.width, c.chart.height);
                }
            });
            Chart.plugins.register({
                afterDraw: function(chart) {
                    if (chart.data.labels.length === 0) {
                        var ctx = chart.chart.ctx;
                        var width = chart.chart.width;
                        var height = chart.chart.height
                        chart.clear();

                        ctx.save();
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.font = "3rem 'Lucida Grande'";
                        ctx.fillText('No data available', width / 2, height / 2);
                        ctx.restore();
                    }
                }

            });

            Chart.Legend.prototype.afterFit = function() {
                var chart_type = this.chart.config.type;
                if (chart_type === "pie" || chart_type === "doughnut") {
                    this.height = this.height;
                } else {
                    this.height = this.height + 20;
                };
            };
        },

        GetUpdateElement: function(id) {
            var self = this;
            var element_data = self.dashboard_data.element_data[id];

            return self._rpc({
                model: 'dashboard_pro.main_dashboard',
                method: 'get_element',
                args: [
                    [element_data.id], self.dashboard_id
                ],
                context: self.getContext(),
            }).then(function(new_item_data) {
                this.dashboard_data.element_data[element_data.id] = new_item_data[element_data.id];
                this.DashboardElementUpdate([element_data.id]);
            }.bind(this));
        },

        ChartColorOptionsRender: function(e) {
            var self = this;
            if (!$(e.currentTarget).parent().hasClass('date_filter_selected')) {
                var $parent = $(e.currentTarget).parent().parent();
                $parent.find('.date_filter_selected').removeClass('date_filter_selected')
                $(e.currentTarget).parent().addClass('date_filter_selected')
                var element_data = self.dashboard_data.element_data[$parent.data().itemId];
                var chart_data = JSON.parse(element_data.chart_data);
                this.ChartColors(e.currentTarget.dataset.chartColor, this.chart_container[$parent.data().itemId], $parent.data().chartType, $parent.data().chartFamily, element_data.bar_chart_stacked, element_data.semi_circle_chart, element_data.show_data_value, chart_data, element_data)
                this._rpc({
                    model: 'dashboard_pro.element',
                    method: 'write',
                    args: [$parent.data().itemId, {
                        "chart_theme_selection": e.currentTarget.dataset.chartColor
                    }],
                }).then(function() {
                    self.dashboard_data.element_data[$parent.data().itemId]['chart_theme_selection'] = e.currentTarget.dataset.chartColor;
                });
            }
        },
        _ChangeDashBoardTheme: function(e){
            var self = this;
            if (self.dashboard_theme == 'light'){
                $(".o_content").css('background-color','#121212');
                $(".dashboard_pro").css('background-color','#121212');
            }
        },

        fetch_data: function() {
            var self = this;
            return this._rpc({
                model: 'dashboard_pro.main_dashboard',
                method: 'get_dashboard_values_to',
                args: [self.dashboard_id],
                context: self.getContext(),
            }).then(function(result) {
                self.dashboard_data = result;
                self.dashboard_data.theme_data = JSON.parse(self.dashboard_data.theme_data)
                self.dashboard_theme_primary_color = GlobalFunction.convert_to_rgba_function(self.dashboard_data.theme_data.dashboard_theme_primary_color);
                self.dashboard_theme_secondary_color = GlobalFunction.convert_to_rgba_function(self.dashboard_data.theme_data.dashboard_theme_secondary_color);
                self.dashboard_theme_font_color = GlobalFunction.convert_to_rgba_function(self.dashboard_data.theme_data.dashboard_theme_font_color);
            });
        },

        on_reverse_breadcrumb: function(state) {
            var self = this;
            this.trigger_up('push_state', {
                controllerID: this.controllerID,
                state: state || {},
            });
            return $.when(self.fetch_data());
        },

        StopClickPropagation: function(e) {
            this.AllowItemClick = false;
        },

        onDashboardMenuContainerShow: function(e) {
            $(e.currentTarget).addClass('dashboard_item_menu_show');
            var element_id = e.currentTarget.dataset.element_id;
            if (this.UpdateDashboard[element_id]){
                clearInterval(this.UpdateDashboard[element_id]);
                delete this.UpdateDashboard[element_id]
            }

            if ($(e.target).hasClass('dashboard_more_action')) {
                var chart_id = e.target.dataset.itemId;
                var name = this.dashboard_data.element_data[chart_id].name;
                var base64_image = this.chart_container[chart_id].toBase64Image();
                $(e.target).find('.dropdown-menu').empty();
                $(e.target).find('.dropdown-menu').append($(QWeb.render('MoreChartOptions', {
                    href: base64_image,
                    download_fileName: name,
                    chart_id: chart_id
                })))
            }
        },

        onDashboardMenuContainerHide: function(e) {
            var self = this;
            $(e.currentTarget).removeClass('dashboard_item_menu_show');
            var element_id = e.currentTarget.dataset.element_id;
            var updateValue = this.dashboard_data.element_data[element_id]["update_element_data_time"];
            if (updateValue) {
                var updateinterval = setInterval(function() {
                    self.GetUpdateElement(element_id)
                }, updateValue);
                self.UpdateDashboard[element_id] = updateinterval;
            }
            if (this.dashboard_data.element_data[element_id]['isDrill'] == true) {
                clearInterval(this.UpdateDashboard[element_id]);
            }
        },

        dark_color_generator: function(color, opacity, percent) {
            var num = parseInt(color.slice(1), 16),
                amt = Math.round(2.55 * percent),
                R = (num >> 16) + amt,
                G = (num >> 8 & 0x00FF) + amt,
                B = (num & 0x0000FF) + amt;
            return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1) + "," + opacity;
        },

        MainDashboardRender: function() {
            var self = this;
            self.$el.empty();
            self.$el.addClass('dashboard_pro d-flex flex-column');
            var $header = $(QWeb.render('DashboardProHeader', {
                dashboard_name: self.dashboard_data.name,
                dashboard_manager: self.dashboard_data.dashboard_manager,
                date_selection_data: self.date_filter_selections,
                date_selection_order: self.date_filter_selection_order,
                all_dashboard_theme: self.dashboard_data.all_theme_data,
                current_dashboard_theme: self.dashboard_data.theme_data['id'],
                dashboard_theme_primary_color: self.dashboard_theme_primary_color,
                dashboard_theme_secondary_color: self.dashboard_theme_secondary_color,
                dashboard_theme_font_color: self.dashboard_theme_font_color,
            }));

            if (!config.device.isMobile) {
                $header.addClass("dashboard_header_sticky")
            }

            self.$el.append($header);
            self.MainDashboardContentRender();
        },

        MainDashboardContentRender: function() {
            var self = this;
            if (self.dashboard_data.element_data) {
                self._renderDateFilterDatePicker();
                self._renderSpecificDateFilterDatePicker();
                self.$el.find('.date_input_fields').addClass("hide");
                self.$el.find('.dashboard_link').removeClass("hide");
                self.$el.find('#dashboard_layout_refresh').removeClass("hide");

                $('.dashboard_items_list').remove();
                var $dashboard_body_container = $(QWeb.render('main_body_container',{
                    dashboard_theme_primary_color: self.dashboard_theme_primary_color
                }))
                var $gridstackContainer = $dashboard_body_container.find(".grid-stack");
                $dashboard_body_container.appendTo(self.$el)
                $gridstackContainer.gridstack(self.gridstack_options);
                self.grid = $gridstackContainer.data('gridstack');

                var items = self.SortItems(self.dashboard_data.element_data);

                self.DashboardElementRender(items);

                self.grid.setStatic(true);

            } else if (!self.dashboard_data.element_data) {
                self.$el.find('.dashboard_link').addClass("hide");
                self.NoItemViewRender();
            }
        },

        SortItems: function(element_data) {
            var items = []
            var self = this;
            var element_data = Object.assign({}, element_data);
            if (self.dashboard_data.grid_configuration) {
                self.gridstackConfig = JSON.parse(self.dashboard_data.grid_configuration);
                var a = Object.values(self.gridstackConfig);
                var b = Object.keys(self.gridstackConfig);
                for (var i = 0; i < a.length; i++) {
                    a[i]['id'] = b[i];
                }
                a.sort(function(a, b) {
                    return (35 * a.y + a.x) - (35 * b.y + b.x);
                });
                for (var i = 0; i < a.length; i++) {
                    if (element_data[a[i]['id']]) {
                        items.push(element_data[a[i]['id']]);
                        delete element_data[a[i]['id']];
                    }
                }
            }

            return items.concat(Object.values(element_data));
        },

        _onClickFullScreenMode: function(e){
            var $target = $(e.currentTarget);
            var data = this.dashboard_data.element_data[$target.data('itemId')];
            this._renderFullScreenMode(data);
        },

        _renderFullScreenMode: function(item){
            this._onClickCloseFullScreen();
            var full_screen_overlay = $(QWeb.render('full_screen_overlay'));
            this.$el.find('.dashboard_main_content').append(full_screen_overlay);
            this.fullScreenOverlay = true;
            this._renderGraph(item);
            this.$el.find('.full_screen_overlay > .chart_container').css({
                'height': 'calc(100% - 50px)',
                'width': '100%',
                'position': 'absolute',
                'top': '20px',
            });
            this.$el.find('.full_screen_overlay').find('.dashboard_chart_container').css({
                'height': '100%'
            });
            this.$el.find('.full_screen_overlay').find('.chart_card_body').siblings().remove();
        },

        _onClickCloseFullScreen: function(){
            this.$el.find('.full_screen_overlay').remove();
            this.fullScreenOverlay = false;
        },

        DashboardElementRender: function(items) {
            var self = this;
            self.$el.find('.print-dashboard-btn').addClass("pro_print_hide");

            if (self.dashboard_data.grid_configuration) {
                self.gridstackConfig = JSON.parse(self.dashboard_data.grid_configuration);
            }
            var item_view;
            var container_class = 'grid-stack-item',
                inner_container_class = 'grid-stack-item-content';
            for (var i = 0; i < items.length; i++) {
                if (self.grid) {
                    if (items[i].type_of_element === 'tile') {
                        var item_view = self.DashboardTileRender(items[i])
                        if (items[i].id in self.gridstackConfig) {
                            self.grid.addWidget($(item_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 2, items[i].id);
                        } else {
                            self.grid.addWidget($(item_view), 0, 0, 8, 2, true, 6, null, 2, 2, items[i].id);
                        }
                    } else if (items[i].type_of_element === 'list_view') {
                        self.ListRender(items[i], self.grid)
                    } else if (items[i].type_of_element === 'kpi') {
                        var $kpi_preview = self.KPIRender(items[i], self.grid)
                        if (items[i].id in self.gridstackConfig) {
                            self.grid.addWidget($kpi_preview, self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 3, items[i].id);
                        } else {
                            self.grid.addWidget($kpi_preview, 0, 0, 6, 2, true, 6, null, 2, 3, items[i].id);
                        }

                    }else if (items[i].type_of_element === 'to_do') {
                        self.ToDoListRender(items[i], self.grid)
                    } else if (items[i].type_of_element == 'add_text' ){
                        var add_text_view = self.AddTextRender(items[i]);
                        if (items[i].id in self.gridstackConfig) {
                            self.grid.addWidget($(add_text_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 25, items[i].id);
                        } else {
                            self.grid.addWidget($(add_text_view), 0, 0, 8, 2, true, 6, null, 2, 25, items[i].id);
                        }
                    }else if (items[i].type_of_element == 'add_link' ){
                        var add_link_view = self.AddLinkRender(items[i]);
                        if (items[i].id in self.gridstackConfig) {
                            self.grid.addWidget($(add_link_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 2, items[i].id);
                        } else {
                            self.grid.addWidget($(add_link_view), 0, 0, 8, 2, true, 6, null, 2, 2, items[i].id);
                        }
                    }else if (items[i].type_of_element == 'add_divider' ){
                        var add_divider_view = self.AddDividerRender(items[i]);
                        if(items[i].add_divider_line == 'horizontal'){
                            if (items[i].id in self.gridstackConfig) {
                                self.grid.addWidget($(add_divider_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, 1, false, 6, null, 1,1, items[i].id);
                            } else {
                                self.grid.addWidget($(add_divider_view), 0, 0, 8, 1, true, 6, null, 1, 1, items[i].id);
                            }
                        }
                        else{
                            if (items[i].id in self.gridstackConfig) {
                                self.grid.addWidget($(add_divider_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, 1,  self.gridstackConfig[items[i].id].height, false, 1, null, 1,20, items[i].id);
                            } else {
                                self.grid.addWidget($(add_divider_view), 0, 0, 1, 2, true, 1, null, 1, 20, items[i].id);
                            }
                        }
                    }else if (items[i].type_of_element == 'add_image' ){
                        var add_image_view = self.AddImageRender(items[i]);
                        if (items[i].id in self.gridstackConfig) {
                            self.grid.addWidget($(add_image_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 20, items[i].id);
                        } else {
                            self.grid.addWidget($(add_image_view), 0, 0, 8, 2, true, 6, null, 2, 20, items[i].id);
                        }
                    }else {
                        self._renderGraph(items[i], self.grid)
                    }
                }
            }
        },
        AddTextRender: function(textElement){
            var self = this;
            var add_text_info;
            var field = textElement;
            var add_text_container_class = 'grid-stack-item';
            var add_text_inner_container_class = 'grid-stack-item-content';
            var rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color)
            var font_style_selection = field.add_text_font_style;
            var font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color)
            var add_text_align_field = field.add_text_align;
            var default_icon_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.default_icon_color);

            textElement.IsDashboardManager = self.dashboard_data.dashboard_manager;
            if(field.add_text_font_style == 'custom'){
                var add_text_bold = (field.add_text_custom_bold == true) ? 'bold' : 'normal';
                var add_text_italic = (field.add_text_custom_italic == true) ? 'italic' : 'normal';
                var add_text_font_size = field.add_text_custom_font_size;
                add_text_info = {
                    name_title: field.name,
                    default_icon: field.default_icon,
                    textElement : textElement,
                    default_icon_color_rgba_format: default_icon_color_rgba_format,
                    main_content : field.add_text_main_content,
                    background_color : rgba_background_color,
                    font_color : font_color_rgba_format,
                    font_style_selection : font_style_selection,
                    add_text_bold : add_text_bold,
                    add_text_italic : add_text_italic,
                    add_text_font_size : add_text_font_size,
                    dashboard_list: self.dashboard_data.dashboard_list,
                    add_text_container_class : add_text_container_class,
                    add_text_align_field : add_text_align_field,
                    add_text_inner_container_class : add_text_inner_container_class
                }
            }else{
                add_text_info = {
                    name_title: field.name,
                    default_icon: field.default_icon,
                    default_icon_color_rgba_format: default_icon_color_rgba_format,
                    main_content : field.add_text_main_content,
                    background_color : rgba_background_color,
                    dashboard_list: self.dashboard_data.dashboard_list,
                    textElement : textElement,
                    add_text_inner_container_class : add_text_inner_container_class,
                    add_text_container_class : add_text_container_class,
                    font_color : font_color_rgba_format,
                    font_style_selection : font_style_selection,
                    add_text_align_field : add_text_align_field,
                    dashboard_list: self.dashboard_data.dashboard_list,
                }
            }
            var add_text_view = $(QWeb.render('add_text_element_main_dashboard',add_text_info));
            return add_text_view;
        },
        AddLinkRender : function(DashboardLinkElement){
            var self = this;
            var add_link_info;
            var prefix = 'http://';
            var field = DashboardLinkElement;
            var add_link_content = field.add_link_content;
            if (add_link_content.substr(0, prefix.length) !== prefix)
            {
                add_link_content = prefix + add_link_content;
            }
            var rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color);
            var font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color);
            var add_link_title = field.add_link_title;
            var add_link_title_name = field.name;
            var add_link_container_class = 'grid-stack-item';
            var add_link_inner_container_class = 'grid-stack-item-content';
            DashboardLinkElement.IsDashboardManager = self.dashboard_data.dashboard_manager;
            add_link_info = {
                add_link_content : add_link_content,
                add_link_content_main : field.add_link_content,
                DashboardLinkElement : DashboardLinkElement,
                background_color : rgba_background_color,
                font_color : font_color_rgba_format,
                add_link_title : add_link_title,
                dashboard_list: self.dashboard_data.dashboard_list,
                add_link_title_name : add_link_title_name,
                add_link_container_class : add_link_container_class,
                add_link_inner_container_class : add_link_inner_container_class,
            }
            var add_link_view = $(QWeb.render('add_link_element_main_dashboard',add_link_info));
            return add_link_view;
        },
        AddDividerRender : function(divider){
            var self = this;
            var add_divider_info;
            var add_divider_container_class = 'grid-stack-item';
            var grid_height = '0';
            var add_divider_inner_container_class = 'grid-stack-item-content';
            divider.IsDashboardManager = self.dashboard_data.dashboard_manager;
            add_divider_info = {
                add_divider_container_class :add_divider_container_class,
                add_divider_inner_container_class : add_divider_inner_container_class,
                divider: divider,
                grid_height : grid_height,
                add_divider_line : divider.add_divider_line,
                dashboard_theme_font_color: self.dashboard_theme_font_color,
            }
            var add_divider_view = $(QWeb.render('add_divider_main_dashboard',add_divider_info));
            return add_divider_view;

        },
        AddImageRender : function(imageElement){
            var self = this;
            var add_image_info,image_main;
            image_main = 'data:image/' + (self.file_type_word[imageElement.add_image_image[0]] || 'png') + ';base64,' + imageElement.add_image_image;
            var add_image_container_class = 'grid-stack-item';
            var add_image_inner_container_class = 'grid-stack-item-content';
            imageElement.IsDashboardManager = self.dashboard_data.dashboard_manager;
            add_image_info = {
                  add_image_container_class : add_image_container_class,
                  add_image_inner_container_class : add_image_inner_container_class,
                  imageElement : imageElement,
                  image_main : image_main,
                  dashboard_list: self.dashboard_data.dashboard_list,
            }
            var add_image_view = $(QWeb.render('add_image_main_dashboard',add_image_info));
            return add_image_view;
        },
        DashboardTileRender: function(tile) {
            var self = this;
            var container_class = 'grid-stack-item';
            var inner_container_class = 'grid-stack-item-content';
            var icon_url, item_view;
            var rgba_background_color, font_color_rgba_format, default_icon_color_rgba_format;
            var style_field, style_image_body_l2, style_domain_count_body, style_button_customize_body,
                style_button_delete_body;

            var data_count = GlobalFunction.number_shorthand_function(tile.data_calculation_value, 1);
            var count = field_utils.format.float(tile.data_calculation_value, Float64Array);
            if (tile.selection_icon_field == "Custom") {
                if (tile.icon[0]) {
                    icon_url = 'data:image/' + (self.file_type_word[tile.icon[0]] || 'png') + ';base64,' + tile.icon;
                } else {
                    icon_url = false;
                }
            }

            tile.IsDashboardManager = self.dashboard_data.dashboard_manager;
            rgba_background_color = GlobalFunction.convert_to_rgba_function(tile.background_color);
            font_color_rgba_format = GlobalFunction.convert_to_rgba_function(tile.font_color);
            default_icon_color_rgba_format = GlobalFunction.convert_to_rgba_function(tile.default_icon_color);
            var dark_border_color = GlobalFunction.convert_to_rgba_function(self.dark_color_generator(tile.background_color.split(',')[0], tile.background_color.split(',')[1], -10));
            style_field = "background-color:" + rgba_background_color + ";color : " + font_color_rgba_format + ";" + "border: 1px solid " + dark_border_color + ";";
            switch (tile.layout) {
                case 'layout1':
                    item_view = QWeb.render('dashboard_item_layout1', {
                        item: tile,
                        style_field: style_field,
                        icon_url: icon_url,
                        default_icon_color_rgba_format: default_icon_color_rgba_format,
                        container_class: container_class,
                        inner_container_class: inner_container_class,
                        dashboard_list: self.dashboard_data.dashboard_list,
                        data_count: data_count,
                        count: count,
                        font_color:font_color_rgba_format,
                        date_selection_data: self.date_specific_filter_selections,
                        date_selection_order: self.date_specific_filter_selection_order
                    });
                    break;

                case 'layout2':
                    var rgba_dark_background_color_l2 = GlobalFunction.convert_to_rgba_function(self.dark_color_generator(tile.background_color.split(',')[0], tile.background_color.split(',')[1], -10));
                    style_image_body_l2 = "background-color:" + rgba_dark_background_color_l2 + ";";
                    item_view = QWeb.render('dashboard_item_layout2', {
                        item: tile,
                        style_image_body_l2: style_image_body_l2,
                        style_field: style_field,
                        icon_url: icon_url,
                        default_icon_color_rgba_format: default_icon_color_rgba_format,
                        container_class: container_class,
                        inner_container_class: inner_container_class,
                        dashboard_list: self.dashboard_data.dashboard_list,
                        data_count: data_count,
                        count: count,
                        font_color:font_color_rgba_format,
                        date_selection_data: self.date_specific_filter_selections,
                        date_selection_order: self.date_specific_filter_selection_order
                    });
                    break;

                case 'layout3':
                    item_view = QWeb.render('dashboard_item_layout3', {
                        item: tile,
                        style_field: style_field,
                        icon_url: icon_url,
                        default_icon_color_rgba_format: default_icon_color_rgba_format,
                        container_class: container_class,
                        inner_container_class: inner_container_class,
                        dashboard_list: self.dashboard_data.dashboard_list,
                        data_count: data_count,
                        count: count,
                        font_color:font_color_rgba_format,
                        date_selection_data: self.date_specific_filter_selections,
                        date_selection_order: self.date_specific_filter_selection_order
                    });
                    break;

                case 'layout4':
                    style_field = "color : " + font_color_rgba_format + ";border : solid;border-width : 1px;border-color:" + rgba_background_color + ";"
                    style_image_body_l2 = "background-color:" + rgba_background_color + ";";
                    style_domain_count_body = "color:" + rgba_background_color + ";";
                    item_view = QWeb.render('dashboard_item_layout4', {
                        item: tile,
                        style_field: style_field,
                        style_image_body_l2: style_image_body_l2,
                        style_domain_count_body: style_domain_count_body,
                        icon_url: icon_url,
                        default_icon_color_rgba_format: default_icon_color_rgba_format,
                        container_class: container_class,
                        inner_container_class: inner_container_class,
                        dashboard_list: self.dashboard_data.dashboard_list,
                        data_count: data_count,
                        count: count,
                        font_color:font_color_rgba_format,
                        date_selection_data: self.date_specific_filter_selections,
                        date_selection_order: self.date_specific_filter_selection_order
                    });
                    break;

                case 'layout5':
                    item_view = QWeb.render('dashboard_item_layout5', {
                        item: tile,
                        style_field: style_field,
                        icon_url: icon_url,
                        default_icon_color_rgba_format: default_icon_color_rgba_format,
                        container_class: container_class,
                        inner_container_class: inner_container_class,
                        dashboard_list: self.dashboard_data.dashboard_list,
                        data_count: data_count,
                        count: count,
                        font_color:font_color_rgba_format,
                        date_selection_data: self.date_specific_filter_selections,
                        date_selection_order: self.date_specific_filter_selection_order
                    });
                    break;

                case 'layout6':
                    default_icon_color_rgba_format = GlobalFunction.convert_to_rgba_function(tile.default_icon_color);
                    item_view = QWeb.render('dashboard_item_layout6', {
                        item: tile,
                        style_image_body_l2: style_image_body_l2,
                        style_field: style_field,
                        icon_url: icon_url,
                        default_icon_color_rgba_format: default_icon_color_rgba_format,
                        container_class: container_class,
                        inner_container_class: inner_container_class,
                        dashboard_list: self.dashboard_data.dashboard_list,
                        data_count: data_count,
                        count: count,
                        font_color:font_color_rgba_format,
                        date_selection_data: self.date_specific_filter_selections,
                        date_selection_order: self.date_specific_filter_selection_order
                    });
                    break;

                case 'state_layout_1':
                    default_icon_color_rgba_format = GlobalFunction.convert_to_rgba_function(tile.default_icon_color);
                    style_field = "background-color:" + rgba_background_color + ";color : " + font_color_rgba_format + ";" + "border: 1px solid " + dark_border_color + ";";
                    item_view = QWeb.render('dashboard_item_state_layout',{
                        item: tile,
                        style_image_body_l2: style_image_body_l2,
                        style_field: style_field,
                        icon_url: icon_url,
                        default_icon_color_rgba_format: default_icon_color_rgba_format,
                        container_class: container_class,
                        inner_container_class: inner_container_class,
                        dashboard_list: self.dashboard_data.dashboard_list,
                        data_count: data_count,
                        count: count,
                        font_color:font_color_rgba_format,
                        date_selection_data: self.date_specific_filter_selections,
                        date_selection_order: self.date_specific_filter_selection_order
                    });
                    break;

                case 'state_layout_2':
                    default_icon_color_rgba_format = GlobalFunction.convert_to_rgba_function(tile.default_icon_color);
                    item_view = QWeb.render('dashboard_item_state_layout_1', {
                        item: tile,
                        style_field: style_field,
                        style_image_body_l2: style_image_body_l2,
                        style_domain_count_body: style_domain_count_body,
                        icon_url: icon_url,
                        default_icon_color_rgba_format: default_icon_color_rgba_format,
                        container_class: container_class,
                        inner_container_class: inner_container_class,
                        dashboard_list: self.dashboard_data.dashboard_list,
                        data_count: data_count,
                        count: count,
                        font_color:font_color_rgba_format,
                        date_selection_data: self.date_specific_filter_selections,
                        date_selection_order: self.date_specific_filter_selection_order
                    });
                    break;

                default:
                    item_view = QWeb.render('dashboard_item_layout_default', {
                        item: tile
                    });
                    break;
            }


            return item_view
        },
        ChartElementGet: function(id) {
            var self = this;
            var element_data = self.dashboard_data.element_data[id];

            return self._rpc({
                model: 'dashboard_pro.main_dashboard',
                method: 'get_element',
                args: [
                    [element_data.id], self.dashboard_id
                ],
                context: self.getContext(),
            }).then(function(new_item_data) {
                this.dashboard_data.element_data[id] = new_item_data[id];
                $(self.$el.find(".grid-stack-item[data-gs-id=" + id + "]").children()[0]).find(".card-body").empty();
                var element_data = self.dashboard_data.element_data[id]
                if (element_data.json_list_data) {
                    var item_view = $(self.$el.find(".grid-stack-item[data-gs-id=" + id + "]").children()[0]);
                    var $container = self.renderListViewData(element_data);
                    item_view.find(".card-body").append($container);
                    var length = JSON.parse(element_data['json_list_data']).data_rows.length
                    if (new_item_data["list_view_type"] === "ungrouped" && JSON.parse(element_data['json_list_data']).data_rows.length) {
                        item_view.find('.pager').removeClass('d-none');
                        if (length < 15) item_view.find('.load_next').addClass('event_offer_list');
                        item_view.find('.value').text("1-" + JSON.parse(element_data['json_list_data']).data_rows.length);
                    } else {
                        item_view.find('.pager').addClass('d-none');
                    }
                } else {
                    self.ChartRender($(self.$el.find(".grid-stack-item[data-gs-id=" + id + "]").children()[0]), element_data);
                }
            }.bind(this));
        },

        onChartMoreInfoClick: function(evt) {
            var self = this;
            var element_id = evt.currentTarget.dataset.itemId;
            var element_data = self.dashboard_data.element_data[element_id];
            var groupBy = element_data.group_chart_field === 'relational_type' ? element_data.chart_relation_groupby_name : element_data.chart_relation_groupby_name + ':' + element_data.chart_group_field;
            var domain = JSON.parse(element_data.chart_data).previous_domain

            if (element_data.show_records) {
                if (element_data.action) {
                    var action = Object.assign({}, element_data.action);
                    if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree', 'list');
                    for (var i = 0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1];
                    action['domain'] = domain || [];
                } else {
                    var action = {
                        name: _t(element_data.name),
                        type: 'ir.actions.act_window',
                        res_model: element_data.model_name,
                        domain: domain || [],
                        context: {
                            'group_by': groupBy,
                        },
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        view_mode: 'list',
                        target: 'current',
                    }
                }
                self.do_action(action, {
                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                });
            }
        },

        NoItemViewRender: function() {
            $('.dashboard_items_list').remove();
            var self = this;
            $(QWeb.render('NoItemView',{
                dashboard_theme_primary_color : self.dashboard_theme_primary_color
            })).appendTo(self.$el)
        },
        onChartCanvasClick: function(evt) {
            var self = this;
            this.fullScreenOverlay = false;
            if (evt.currentTarget.classList.value !== 'list_canvas_click') {
                var element_id = evt.currentTarget.dataset.chartId;
                if (element_id in self.UpdateDashboard) {
                    clearInterval(self.UpdateDashboard[element_id]);
                    delete self.UpdateDashboard[element_id]
                }
                var myChart = self.chart_container[element_id];
                var activePoint = myChart.getElementAtEvent(evt)[0];
                if (activePoint) {
                    var element_data = self.dashboard_data.element_data[element_id];
                    var groupBy = JSON.parse(element_data["chart_data"])['groupby'];
                    if (activePoint._chart.data.domains) {
                        var sequnce = element_data.sequnce ? element_data.sequnce : 0;

                        var domain = activePoint._chart.data.domains[activePoint._index]
                        if (element_data.max_sequnce != 0 && sequnce < element_data.max_sequnce) {
                            self._rpc({
                                model: 'dashboard_pro.element',
                                method: 'get_data_main_func',
                                args: [element_id, domain, sequnce]
                            }).then(function(result) {
                                self.dashboard_data.element_data[element_id]['sequnce'] = result.sequence;
                                self.dashboard_data.element_data[element_id]['isDrill'] = true;
                                if (result.chart_data) {
                                    self.dashboard_data.element_data[element_id]['type_of_element'] = result.chart_type;
                                    self.dashboard_data.element_data[element_id]['chart_data'] = result.chart_data;
                                    if (self.dashboard_data.element_data[element_id].domains) {
                                        self.dashboard_data.element_data[element_id]['domains'][result.sequence] = JSON.parse(result.chart_data).previous_domain;
                                    } else {
                                        self.dashboard_data.element_data[element_id]['domains'] = {}
                                        self.dashboard_data.element_data[element_id]['domains'][result.sequence] = JSON.parse(result.chart_data).previous_domain;
                                    }
                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_item_chart_info").removeClass('d-none')
                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_color_option").removeClass('d-none')
                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_more_action").addClass('d-none');

                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".card-body").empty();
                                    var element_data = self.dashboard_data.element_data[element_id]
                                    self.ChartRender($(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]), element_data);
                                } else {
                                    if ('domains' in self.dashboard_data.element_data[element_id]) {
                                        self.dashboard_data.element_data[element_id]['domains'][result.sequence] = JSON.parse(result.json_list_data).previous_domain;
                                    } else {
                                        self.dashboard_data.element_data[element_id]['domains'] = {}
                                        self.dashboard_data.element_data[element_id]['domains'][result.sequence] = JSON.parse(result.json_list_data).previous_domain;
                                    }
                                    self.dashboard_data.element_data[element_id]['isDrill'] = true;
                                    self.dashboard_data.element_data[element_id]['sequnce'] = result.sequence;
                                    self.dashboard_data.element_data[element_id]['json_list_data'] = result.json_list_data;
                                    self.dashboard_data.element_data[element_id]['list_view_type'] = result.list_view_type;
                                    self.dashboard_data.element_data[element_id]['type_of_element'] = 'list_view';

                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_item_chart_info").addClass('d-none')
                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_color_option").addClass('d-none')
                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".card-body").empty();

                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_more_action").addClass('d-none');
                                    var element_data = self.dashboard_data.element_data[element_id]
                                    var $container = self.renderListViewData(element_data);
                                    $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".card-body").append($container).addClass('overflow');
                                }
                            });
                        } else {
                            if (element_data.action) {
                                var action = Object.assign({}, element_data.action);
                                if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree', 'list');
                                for (var i = 0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1];
                                action['domain'] = domain || [];
                            } else {
                                var action = {
                                    name: _t(element_data.name),
                                    type: 'ir.actions.act_window',
                                    res_model: element_data.model_name,
                                    domain: domain || [],
                                    context: {
                                        'group_by': groupBy,
                                    },
                                    views: [
                                        [false, 'list'],
                                        [false, 'form']
                                    ],
                                    view_mode: 'list',
                                    target: 'current',
                                }
                            }
                            if (element_data.show_records) {
                                self.do_action(action, {
                                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                                });
                            }
                        }
                    }
                }
            } else {
                var element_id = $(evt.target).parent().data().itemId;
                if (this.UpdateDashboard[element_id]) {
                    clearInterval(this.UpdateDashboard[element_id]);
                    delete self.UpdateDashboard[element_id];
                }
                var element_data = self.dashboard_data.element_data[element_id]
                if (self.dashboard_data.element_data[element_id].max_sequnce) {

                    var sequence = element_data.sequnce ? element_data.sequnce : 0

                    var domain = $(evt.target).parent().data().domain;

                    if ($(evt.target).parent().data().last_seq !== sequence) {
                        self._rpc({
                            model: 'dashboard_pro.element',
                            method: 'get_data_main_func',
                            args: [element_id, domain, sequence]
                        }).then(function(result) {
                            if (result.json_list_data) {
                                if (self.dashboard_data.element_data[element_id].domains) {
                                    self.dashboard_data.element_data[element_id]['domains'][result.sequence] = JSON.parse(result.json_list_data).previous_domain;
                                } else {
                                    self.dashboard_data.element_data[element_id]['domains'] = {}
                                    self.dashboard_data.element_data[element_id]['domains'][result.sequence] = JSON.parse(result.json_list_data).previous_domain;
                                }
                                self.dashboard_data.element_data[element_id]['isDrill'] = true;
                                self.dashboard_data.element_data[element_id]['sequnce'] = result.sequence;
                                self.dashboard_data.element_data[element_id]['json_list_data'] = result.json_list_data;
                                self.dashboard_data.element_data[element_id]['list_view_type'] = result.list_view_type;
                                self.dashboard_data.element_data[element_id]['type_of_element'] = 'list_view';

                                self.dashboard_data.element_data[element_id]['sequnce'] = result.sequence;
                                $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_item_action_export").addClass('d-none');

                                var element_data = self.dashboard_data.element_data[element_id]
                                var $container = self.renderListViewData(element_data);
                                $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".card-body").append($container);
                            } else {
                                self.dashboard_data.element_data[element_id]['chart_data'] = result.chart_data;
                                self.dashboard_data.element_data[element_id]['sequnce'] = result.sequence;
                                self.dashboard_data.element_data[element_id]['type_of_element'] = result.chart_type;
                                self.dashboard_data.element_data[element_id]['isDrill'] = true;
                                if (self.dashboard_data.element_data[element_id].domains) {
                                    self.dashboard_data.element_data[element_id]['domains'][result.sequence] = JSON.parse(result.chart_data).previous_domain;
                                } else {
                                    self.dashboard_data.element_data[element_id]['domains'] = {}
                                    self.dashboard_data.element_data[element_id]['domains'][result.sequence] = JSON.parse(result.chart_data).previous_domain;
                                }
                                $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_item_chart_info").removeClass('d-none')
                                $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_color_option").removeClass('d-none')
                                $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".dashboard_item_action_export").addClass('d-none');
                                $(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]).find(".card-body").empty();
                                var element_data = self.dashboard_data.element_data[element_id]
                                self.ChartRender($(self.$el.find(".grid-stack-item[data-gs-id=" + element_id + "]").children()[0]), element_data);
                            }
                        });
                    }
                }
            }
            evt.stopPropagation();
        },

        _RenderEditMode: function() {
            var self = this;

            self.remove_time_diff();

            $('#dashboard_title_input').val(self.dashboard_data.name);

            $('.am_element').addClass("hide");
            $('.em_element').removeClass("hide");

            self.$el.find('.element_click').addClass('element_not_click').removeClass('element_click');
            self.$el.find('.dashboard_element').removeClass('dashboard_element_hover');
            self.$el.find('.dashboard_element_header').removeClass('dashboard_element_hover');

            self.$el.find('.dashboard_element_layout_2').removeClass('dashboard_element_hover');
            self.$el.find('.dashboard_element_header_layout_2').removeClass('dashboard_element_hover');

            self.$el.find('.dashboard_element_layout_5').removeClass('dashboard_element_hover');

            self.$el.find('.dashboard_element_buttons_container').removeClass('dashboard_element_hover');

            self.$el.find('.dashboard_link').addClass("hide")
            self.$el.find('.dashboard_top_settings').addClass("hide")
            self.$el.find('.theme_group').addClass("hide")
            self.$el.find('.dashboard_edit_mode_settings').removeClass("hide")

            self.$el.find('.start_tv_dashboard').addClass('hide');
            self.$el.find('.chart_container').addClass('element_not_click');
            self.$el.find('.list_view_container').addClass('element_not_click');

            if (self.grid) {
                self.grid.enable();
            }
        },
        _ToggleEditMode: function() {
            var self = this
            if (self.DashboardEditMode) {
                self._RenderActiveMode()
                self.DashboardEditMode = false
            } else if (!self.DashboardEditMode) {
                self._RenderEditMode()
                self.DashboardEditMode = true
            }

        },

        AddElementDashboard: function(e) {
            var self = this;
            if (e.currentTarget.dataset.item !== "json") {
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'dashboard_pro.element',
                    view_id: 'dashboard_pro_list_form_view',
                    views: [
                        [false, 'form']
                    ],
                    target: 'current',
                    context: {
                        'dashboard_id': self.dashboard_id,
                        'type_of_element': e.currentTarget.dataset.item,
                        'form_view_ref': 'openeducat_dashboard_kpi.item_form_view',
                        'form_view_initial_mode': 'edit',
                        'interval_time': self.dashboard_data.interval_time,
                    },
                }, {
                    on_reverse_breadcrumb: this.on_reverse_breadcrumb,
                });
            } else {
                self.JsonElementImport(e);
            }
        },
        DashboardThemeSelection: function(e){
            var self = this;
            if (e.currentTarget.dataset.theme === "new") {
                self.do_action({
                    name:_t('Themes'),
                    type: 'ir.actions.act_window',
                    res_model: 'dashboard_pro.theme',
                    view_id: 'dashboard_pro_theme_form_view',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current',
                }, {
                    on_reverse_breadcrumb: this.on_reverse_breadcrumb,
                });
            }else{
                var theme_id = e.currentTarget.id;
                this._rpc({
                    model: 'dashboard_pro.main_dashboard',
                    method: 'change_dashboard_theme_func',
                    args: [self.dashboard_id,parseInt(theme_id)],
                }).then(function(result) {
                    self.action_manager.notifications.add(
                        _t( 'Changed Dashboard Theme To '+ result),{
                            type: 'warning',
                            title: _t("Dashboard Theme")
                    });
                    $.when(self.fetch_data()).then(function() {
                        self.remove_time_diff();
                        self.MainDashboardRender();
                        self.update_time_diff();
                    });
                });
            }
        },
        JsonElementImport: function(e) {
            var self = this;
            $('.input_import_item_button').click();
        },

        importElement: function(e) {
            var self = this;
            var fileReader = new FileReader();
            fileReader.onload = function() {
                $('.input_import_item_button').val('');
                framework.blockUI();
                self._rpc({
                    model: 'dashboard_pro.main_dashboard',
                    method: 'import_item',
                    args: [self.dashboard_id],
                    kwargs: {
                        file: fileReader.result,
                        dashboard_id: self.dashboard_id
                    }
                }).then(function(result) {
                    if (result === "Success") {

                        $.when(self.fetch_data()).then(function() {
                            self.MainDashboardRender();
                            framework.unblockUI();
                        });
                    }
                });
            };
            fileReader.readAsText($('.input_import_item_button').prop('files')[0]);
        },

        _onAddLayoutClick: function() {
            var self = this;

            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'dashboard_pro.element',
                view_id: 'dashboard_pro_list_form_view',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                context: {
                    'dashboard_id': self.dashboard_id,
                    'form_view_ref': 'openeducat_dashboard_kpi.item_form_view',
                    'form_view_initial_mode': 'edit',
                },
            }, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });
        },

        _onEditLayoutClick: function() {
            var self = this;
            self._RenderEditMode();
        },
        _RenderActiveMode: function() {
            var self = this

            if (self.grid) {
                $('.grid-stack').data('gridstack').disable();
            }

            $('#dashboard_title_label').text(self.dashboard_data.name);

            $('.am_element').removeClass("hide");
            $('.em_element').addClass("hide");
            if (self.dashboard_data.element_data) $('.am_content_element').removeClass("hide");

            self.$el.find('.element_not_click').addClass('element_click').removeClass('element_not_click')
            self.$el.find('.dashboard_element').addClass('dashboard_element_hover')
            self.$el.find('.dashboard_element_header').addClass('dashboard_element_hover')

            self.$el.find('.dashboard_element_layout_2').addClass('dashboard_element_hover')
            self.$el.find('.dashboard_element_header_layout_2').addClass('dashboard_element_hover')

            self.$el.find('.dashboard_element_layout_5').addClass('dashboard_element_hover')


            self.$el.find('.dashboard_element_buttons_container').addClass('dashboard_element_hover');

            self.$el.find('.dashboard_top_settings').removeClass("hide")
            self.$el.find('.dashboard_edit_mode_settings').addClass("hide")
            self.$el.find('.theme_group').removeClass("hide")

            self.$el.find('.start_tv_dashboard').removeClass('hide');
            self.$el.find('.chart_container').removeClass('element_not_click element_click');
            self.$el.find('.list_view_container').removeClass('element_click');

            self.update_time_diff();
        },
        _onSaveLayoutClick: function() {
            var self = this;
            var dashboard_title = $('#dashboard_title_input').val();
            if (dashboard_title != false && dashboard_title != 0 && dashboard_title !== self.dashboard_data.name) {
                self.dashboard_data.name = dashboard_title;
                this._rpc({
                    model: 'dashboard_pro.main_dashboard',
                    method: 'write',
                    args: [self.dashboard_id, {
                        'name': dashboard_title
                    }],
                })
            }
            if (this.dashboard_data.element_data) self.SaveLayout();
            self._RenderActiveMode();
        },

        CancelLayout: function() {
            var self = this;
            $.when(self.fetch_data()).then(function() {
                self.MainDashboardRender();
                self.update_time_diff();
            });
        },

        ElementClick: function(e) {
            var self = this;
            if (self.AllowItemClick) {
                e.preventDefault();
                if (e.target.title != "Edit Element") {
                    var element_id = parseInt(e.currentTarget.firstElementChild.id);
                    var element_data = self.dashboard_data.element_data[element_id];
                    if (element_data.show_records) {
                        if (element_data.action) {
                            var action = Object.assign({}, element_data.action);
                            if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree', 'list');
                            for (var i = 0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1];
                            action['domain'] = element_data.domain || [];

                        } else {
                            var action = {
                                name: _t(element_data.name),
                                type: 'ir.actions.act_window',
                                res_model: element_data.model_name,
                                domain: element_data.domain || "[]",
                                views: [
                                   [false, 'list'],
                                    [false, 'form']
                                ],
                                view_mode: 'list',
                                target: 'current',
                            }
                        }
                        try{
                            if(action.res_model == false && element_data.type_of_element != 'add_text' && element_data.type_of_element != 'add_link') throw "Look Like Model Is Empty For Current Item! Please Select Model!"
                            self.do_action(action, {
                                on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                            });
                        }catch(err){
                            alert(err);
                        }
                    }
                }
            } else {
                self.AllowItemClick = true;
            }
        },

        ElementCustomization: function(e) {
            var self = this;
            var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'))
            self.ElementFormView(id);

            e.stopPropagation();
        },

        ElementFormView: function(id) {
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'dashboard_pro.element',
                view_id: 'dashboard_pro_list_form_view',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                context: {
                    'form_view_ref': 'openeducat_dashboard_kpi.item_form_view',
                    'form_view_initial_mode': 'edit',
                },
                res_id: id
            }, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });
        },

        DashboardElementUpdate: function(ids) {
            var self = this;
            for (var i = 0; i < ids.length; i++) {

                var element_data = self.dashboard_data.element_data[ids[i]]
                if (element_data['type_of_element'] == 'list_view') {
                    var item_view = self.$el.find(".grid-stack-item[data-gs-id=" + element_data.id + "]");
                    item_view.find('.card-body').empty();
                    item_view.find('.card-body').append(self.renderListViewData(element_data));
                    var length = JSON.parse(element_data['json_list_data']).data_rows.length;
                    if (element_data['list_view_type'] === 'ungrouped' && JSON.parse(element_data['json_list_data']).data_rows.length) {
                        if (item_view.find('.pager_name')) {
                            item_view.find('.pager_name').empty();
                            var $pager_container = QWeb.render('pager_template', {
                                element_id: ids[i],
                                intial_count: 15,
                                offset : 1
                            })
                            item_view.find('.pager_name').append($($pager_container));
                        }
                        if (length < 15) item_view.find('.load_next').addClass('event_offer_list');
                        item_view.find('.value').text("1-" + JSON.parse(element_data['json_list_data']).data_rows.length);
                    } else {
                        item_view.find('.pager').addClass('d-none');
                    }
                } else if (element_data['type_of_element'] == 'tile') {
                    var item_view = self.DashboardTileRender(element_data);
                    self.$el.find(".grid-stack-item[data-gs-id=" + element_data.id + "]").empty();
                    self.$el.find(".grid-stack-item[data-gs-id=" + element_data.id + "]").append($(item_view).find('.dashboarditem_id'));
                } else if (element_data['type_of_element'] == 'kpi') {
                    var item_view = self.KPIRender(element_data);
                    self.$el.find(".grid-stack-item[data-gs-id=" + element_data.id + "]").empty();
                    self.$el.find(".grid-stack-item[data-gs-id=" + element_data.id + "]").append($(item_view).find('.dashboarditem_id'));
                } else {
                    self.grid.removeWidget(self.$el.find(".grid-stack-item[data-gs-id=" + element_data.id + "]"));
                    self.DashboardElementRender([element_data]);
                }

            }
            self.grid.setStatic(true);
        },
        HideFunction: function(options, item, ChartFamily, chartType) {
            return options;
        },

        ChartColors: function(palette, MyChart, ChartType, ChartFamily, stack, semi_circle, show_data_value, chart_data, item) {
            chart_data;
            var self = this;
            var currentPalette = "cool";
            if (!palette) palette = currentPalette;
            currentPalette = palette;

            var gradient;
            switch (palette) {
                case 'cool':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [220, 237, 200, 1],
                        45: [66, 179, 213, 1],
                        65: [26, 39, 62, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'warm':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [254, 235, 101, 1],
                        45: [228, 82, 27, 1],
                        65: [77, 52, 47, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'neon':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [255, 236, 179, 1],
                        45: [232, 82, 133, 1],
                        65: [106, 27, 154, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;

                case 'default':
                    var color_set = ['#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600', '#8a79fd', '#b1b5be', '#1c425c', '#8c2620', '#71ecef', '#0b4295', '#f2e6ce', '#1379e7']
            }

            var chartType = MyChart.config.type;
            switch (chartType) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    if (MyChart.config.data.datasets[0]){
                        var datasets = MyChart.config.data.datasets[0];
                        var setsCount = datasets.data.length;
                    }
                    break;

                case "bar":
                case "horizontalBar":
                case "line":
                    if (MyChart.config.data.datasets[0]){
                        var datasets = MyChart.config.data.datasets;
                        var setsCount = datasets.length;
                    }
                    break;
            }

            var chartColors = [];

            if (palette !== "default") {
                var gradientKeys = Object.keys(gradient);
                gradientKeys.sort(function(a, b) {
                    return +a - +b;
                });
                for (var i = 0; i < setsCount; i++) {
                    var gradientIndex = (i + 1) * (100 / (setsCount + 1));
                    for (var j = 0; j < gradientKeys.length; j++) {
                        var gradientKey = gradientKeys[j];
                        if (gradientIndex === +gradientKey) {
                            chartColors[i] = 'rgba(' + gradient[gradientKey].toString() + ')';
                            break;
                        } else if (gradientIndex < +gradientKey) {
                            var prevKey = gradientKeys[j - 1];
                            var gradientPartIndex = (gradientIndex - prevKey) / (gradientKey - prevKey);
                            var color = [];
                            for (var k = 0; k < 4; k++) {
                                color[k] = gradient[prevKey][k] - ((gradient[prevKey][k] - gradient[gradientKey][k]) * gradientPartIndex);
                                if (k < 3) color[k] = Math.round(color[k]);
                            }
                            chartColors[i] = 'rgba(' + color.toString() + ')';
                            break;
                        }
                    }
                }
            } else {
                for (var i = 0, counter = 0; i < setsCount; i++, counter++) {
                    if (counter >= color_set.length) counter = 0;

                    chartColors.push(color_set[counter]);
                }
            }

            var datasets = MyChart.config.data.datasets;
            var options = MyChart.config.options;

            options.legend.labels.usePointStyle = true;
            if (ChartFamily == "circle") {
                if (show_data_value) {
                    options.legend.position = 'bottom';
                    options.layout.padding.top = 10;
                    options.layout.padding.bottom = 20;
                    options.layout.padding.left = 20;
                    options.layout.padding.right = 20;
                } else {
                    options.legend.position = 'top';
                }

                options = self.HideFunction(options, item, ChartFamily, chartType);

                options.plugins.datalabels.align = 'center';
                options.plugins.datalabels.anchor = 'end';
                options.plugins.datalabels.borderColor = 'white';
                options.plugins.datalabels.borderRadius = 25;
                options.plugins.datalabels.borderWidth = 2;
                options.plugins.datalabels.clamp = true;
                options.plugins.datalabels.clip = false;

                options.tooltips.callbacks = {
                    title: function(tooltipItem, data) {
                        var self = self;
                        var k_amount = data.datasets[tooltipItem[0].datasetIndex]['data'][tooltipItem[0].index];
                        var selection = chart_data.selection;
                        if (selection === 'monetary') {
                            var currency_id = chart_data.currency;
                            k_amount = GlobalFunction.currency_monetary_function(k_amount, currency_id);
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount
                        } else if (selection === 'custom') {
                            var field = chart_data.field;
                            k_amount = field_utils.format.float(k_amount, Float64Array);
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount + " " + field;
                        } else {
                            k_amount = field_utils.format.float(k_amount, Float64Array);
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount
                        }
                    },
                    label: function(tooltipItem, data) {
                        return data.labels[tooltipItem.index];
                    },
                }
                for (var i = 0; i < datasets.length; i++) {
                    datasets[i].backgroundColor = chartColors;
                    datasets[i].borderColor = "rgba(255,255,255,1)";
                }
                if (semi_circle && (chartType === "pie" || chartType === "doughnut")) {
                    options.rotation = 1 * Math.PI;
                    options.circumference = 1 * Math.PI;
                }
            } else if (ChartFamily == "square") {
                options = self.HideFunction(options, item, ChartFamily, chartType);

                options.scales.xAxes[0].gridLines.display = false;
                options.scales.yAxes[0].ticks.beginAtZero = true;

                options.plugins.datalabels.align = 'end';

                options.plugins.datalabels.formatter = function(value, ctx) {
                    var selection = chart_data.selection;
                    if (selection === 'monetary') {
                        var currency_id = chart_data.currency;
                        var data = GlobalFunction.number_shorthand_function(value, 1);
                        data = GlobalFunction.currency_monetary_function(data, currency_id);
                        return data;
                    } else if (selection === 'custom') {
                        var field = chart_data.field;
                        return GlobalFunction.number_shorthand_function(value, 1) + ' ' + field;
                    } else {
                        return GlobalFunction.number_shorthand_function(value, 1);
                    }
                };

                if (chartType === "line") {
                    options.plugins.datalabels.backgroundColor = function(context) {
                        return context.dataset.borderColor;
                    };
                }

                if (chartType === "horizontalBar") {
                    options.scales.xAxes[0].ticks.callback = function(value, index, values) {
                        var selection = chart_data.selection;
                        if (selection === 'monetary') {
                            var currency_id = chart_data.currency;
                            var data = GlobalFunction.number_shorthand_function(value, 1);
                            data = GlobalFunction.currency_monetary_function(data, currency_id);
                            return data;
                        } else if (selection === 'custom') {
                            var field = chart_data.field;
                            return GlobalFunction.number_shorthand_function(value, 1) + ' ' + field;
                        } else {
                            return GlobalFunction.number_shorthand_function(value, 1);
                        }
                    }
                    options.scales.xAxes[0].ticks.beginAtZero = true;
                } else {
                    options.scales.yAxes[0].ticks.callback = function(value, index, values) {
                        var selection = chart_data.selection;
                        if (selection === 'monetary') {
                            var currency_id = chart_data.currency;
                            var data = GlobalFunction.number_shorthand_function(value, 1);
                            data = GlobalFunction.currency_monetary_function(data, currency_id);
                            return data;
                        } else if (selection === 'custom') {
                            var field = chart_data.field;
                            var field = chart_data.field;
                            return GlobalFunction.number_shorthand_function(value, 1) + ' ' + field;
                        } else {
                            return GlobalFunction.number_shorthand_function(value, 1);
                        }
                    }
                }

                options.tooltips.callbacks = {
                    label: function(tooltipItem, data) {
                        var self = self;
                        var k_amount = data.datasets[tooltipItem.datasetIndex]['data'][tooltipItem.index];
                        var selection = chart_data.selection;
                        if (selection === 'monetary') {
                            var currency_id = chart_data.currency;
                            k_amount = GlobalFunction.currency_monetary_function(k_amount, currency_id);
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount
                        } else if (selection === 'custom') {
                            var field = chart_data.field;
                            k_amount = field_utils.format.float(k_amount, Float64Array);
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount + " " + field;
                        } else {
                            k_amount = field_utils.format.float(k_amount, Float64Array);
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount
                        }
                    }
                }

                for (var i = 0; i < datasets.length; i++) {
                    switch (ChartType) {
                        case "bar":
                        case "horizontalBar":
                            if (datasets[i].type && datasets[i].type == "line") {
                                datasets[i].borderColor = chartColors[i];
                                datasets[i].backgroundColor = "rgba(255,255,255,0)";
                                datasets[i]['datalabels'] = {
                                    backgroundColor: chartColors[i],
                                }
                            } else {
                                datasets[i].backgroundColor = chartColors[i];
                                datasets[i].borderColor = "rgba(255,255,255,0)";
                                options.scales.xAxes[0].stacked = stack;
                                options.scales.yAxes[0].stacked = stack;
                            }
                            break;
                        case "line":
                            datasets[i].borderColor = chartColors[i];
                            datasets[i].backgroundColor = "rgba(255,255,255,0)";
                            break;
                        case "area":
                            datasets[i].borderColor = chartColors[i];
                            break;
                    }
                }

            }
            MyChart.update();
        },
        OnRefreshButton : function(){
            var self = this;
            $.when(self.fetch_data()).then(function() {
                    self.DashboardElementUpdate(Object.keys(self.dashboard_data.element_data));
            });
        },
        DeleteElement: function(e) {
            var self = this;
            var item = $($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0])
            var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'));
            self.DeleteElementFunc(id, item);
            e.stopPropagation();
        },

        DeleteElementFunc: function(id, item) {
            var self = this;
            Dialog.confirm(this, (_t("Are you sure you want to remove this item?")), {
                confirm_callback: function() {

                    self._rpc({
                        model: 'dashboard_pro.element',
                        method: 'unlink',
                        args: [id],
                    }).then(function(result) {

                        self.remove_time_diff();
                        delete self.dashboard_data.element_data[id];
                        self.grid.removeWidget(item);
                        self.update_time_diff();

                        if (Object.keys(self.dashboard_data.element_data).length > 0) {
                            self.SaveLayout();
                        } else {
                            self.NoItemViewRender();
                        }
                    });
                },
            });
        },

        SaveLayout: function() {
            var self = this;
            var items = $('.grid-stack').data('gridstack').grid.nodes;
            var grid_config = {}

            if (self.dashboard_data.grid_configuration) {
                _.extend(grid_config, JSON.parse(self.dashboard_data.grid_configuration))
            }
            for (var i = 0; i < items.length; i++) {
                grid_config[items[i].id] = {
                    'x': items[i].x,
                    'y': items[i].y,
                    'width': items[i].width,
                    'height': items[i].height
                }
            }

            self.dashboard_data.grid_configuration = JSON.stringify(grid_config);
            this._rpc({
                model: 'dashboard_pro.main_dashboard',
                method: 'write',
                args: [self.dashboard_id, {
                    "grid_configuration": JSON.stringify(grid_config)
                }],
            });
        },

        ListRender: function(item, grid) {
            var self = this;
            var json_list_data = JSON.parse(item.json_list_data),
                pager = item.list_view_type === "ungrouped" ? true : false,
                element_id = item.id,
                data_rows = json_list_data.data_rows,
                length = data_rows ? data_rows.length: 0,
                item_title = item.name;
            var $ItemContainer = self.renderListViewData(item)
            var $gridstack_container = $(QWeb.render('gridstack_list_view_container', {
                chart_title: item_title,
                IsDashboardManager: self.dashboard_data.dashboard_manager,
                dashboard_list: self.dashboard_data.dashboard_list,
                element_id: element_id,
                count: '1-' + length,
                offset: 1,
                intial_count: length,
                pager: pager,
                date_selection_data: self.date_specific_filter_selections,
                date_selection_order: self.date_specific_filter_selection_order
            })).addClass('dashboarditem_id');

            if (length < 15) {
                $gridstack_container.find('.load_next').addClass('event_offer_list');
            }
            if (length == 0){
                $gridstack_container.find('.pager').addClass('d-none');
            }
            $gridstack_container.find('.card-body').append($ItemContainer);
            if (pager){
                $gridstack_container.find('.list_canvas_click').removeClass('list_canvas_click');
            }

            item.$el = $gridstack_container;
            if (element_id in self.gridstackConfig) {
                grid.addWidget($gridstack_container, self.gridstackConfig[element_id].x, self.gridstackConfig[element_id].y, self.gridstackConfig[element_id].width, self.gridstackConfig[element_id].height, false, 12, null, 3, null, element_id);
            } else {
                grid.addWidget($gridstack_container, 0, 0, 13, 4, true, 12, null, 3, null, element_id);
            }
        },

        renderListViewData: function(item) {
            var self = this;
            var json_list_data = JSON.parse(item.json_list_data);
            var element_id = item.id,
                data_rows = json_list_data.data_rows,
                item_title = item.name;
            if (item.list_view_type === "ungrouped" && json_list_data) {
                if (json_list_data.date_index) {
                    var index_data = json_list_data.date_index;
                    for (var i = 0; i < index_data.length; i++) {
                        for (var j = 0; j < json_list_data.data_rows.length; j++) {
                            var index = index_data[i]
                            var date = json_list_data.data_rows[j]["data"][index]
                            if (date) json_list_data.data_rows[j]["data"][index] = field_utils.format.datetime(moment(moment(date).utc(true)._d), {}, {
                                timezone: false
                            });
                            else json_list_data.data_rows[j]["data"][index] = "";
                        }
                    }
                }
            }
            if (json_list_data) {
                for (var i = 0; i < json_list_data.data_rows.length; i++) {
                    for (var j = 0; j < json_list_data.data_rows[0]["data"].length; j++) {
                        if (typeof(json_list_data.data_rows[i].data[j]) === "number" || json_list_data.data_rows[i].data[j]) {
                            if (typeof(json_list_data.data_rows[i].data[j]) === "number") {
                                json_list_data.data_rows[i].data[j] = field_utils.format.float(json_list_data.data_rows[i].data[j], Float64Array)
                            }
                        } else {
                            json_list_data.data_rows[i].data[j] = "";
                        }
                    }
                }
            }
            var $ItemContainer = $(QWeb.render('list_view_table', {
                json_list_data: json_list_data,
                element_id: element_id,
                list_type: item.list_view_type,
                date_selection_data: self.date_specific_filter_selections,
                date_selection_order: self.date_specific_filter_selection_order
            }));
            this.list_container = $ItemContainer;

            if (item.list_view_type === "ungrouped") {
                $ItemContainer.find('.list_canvas_click').removeClass('list_canvas_click');
            }

            if (!item.show_records) {
                $ItemContainer.find('#item_info').hide();
            }
            return $ItemContainer
        },

        ToDoListRender: function(item,grid){
            var self = this;
            var json_todo_list_data = JSON.parse(item.json_todo_list_data),
                element_id = item.id,
                data_rows = json_todo_list_data.data_rows,
                item_title = item.name;
            var $ToDoItemContainer = self.renderToDoListViewData(item);
            var $gridstack_container = $(QWeb.render('to_do_grid_stack_list_view_container', {
                chart_title: item_title,
                IsDashboardManager: self.dashboard_data.dashboard_manager,
                dashboard_list: self.dashboard_data.dashboard_list,
                element_id: element_id,
            })).addClass('dashboarditem_id');

            if (length < 15) {
                $gridstack_container.find('.load_next').addClass('event_offer_list');
            }
            if (length == 0){
                $gridstack_container.find('.pager').addClass('d-none');
            }
            $gridstack_container.find('.card-body').append($ToDoItemContainer);

            item.$el = $gridstack_container;
            if (element_id in self.gridstackConfig) {
                grid.addWidget($gridstack_container, self.gridstackConfig[element_id].x, self.gridstackConfig[element_id].y, self.gridstackConfig[element_id].width, self.gridstackConfig[element_id].height, false, 12, null, 3, null, element_id);
            } else {
                grid.addWidget($gridstack_container, 0, 0, 13, 4, true, 12, null, 3, null, element_id);
            }
        },
        renderToDoListViewData : function(item){
            var self = this;
            var to_do_list_name =  item.name;
            var json_todo_list_data = JSON.parse(item.json_todo_list_data);
            var $ToDoListViewContainer = $(QWeb.render('to_do_list_view_table', {
                to_do_list_name: to_do_list_name,
                json_todo_list_data: json_todo_list_data,
            }));

            return $ToDoListViewContainer;
        },
        DeleteToDoList : function(e){
            var self = this;
            var element_id = e.currentTarget.dataset.itemId;
            this._rpc({
                model: 'to_do.list',
                method: 'to_do_list_delete_func',
                args: [parseInt(element_id)],
            }).then(function(result) {
                self.action_manager.notifications.add(
                    _t( result + ' Is Removed From List.'),{
                        type: 'warning',
                        title: _t("To-Do List")
                });
                $.when(self.fetch_data()).then(function() {
                    self.remove_time_diff();
                    self.MainDashboardRender();
                    self.update_time_diff();
                });
            })
        },
        ChangeToDoState: function(e){
            var self = this;
            var element_id = e.currentTarget.dataset.recordId;
            var state = e.currentTarget.dataset.state;
            this._rpc({
                model: 'to_do.list',
                method: 'to_do_list_state_change_func',
                args: [parseInt(element_id), state],
            }).then(function(result) {
                $.when(self.fetch_data()).then(function() {
                    self.remove_time_diff();
                    self.MainDashboardRender();
                    self.update_time_diff();
                });
            })
        },
        Sum: function(count_1, count_2, item_info, field, target_1, $kpi_preview, kpi_data) {
            var self = this;
            var count = count_1 + count_2;
            item_info['count'] = GlobalFunction.number_shorthand_function(count, 1);
            item_info['count_tooltip'] = count;
            item_info['target_enable'] = field.is_goal_enable;
            var color = (target_1 - count) > 0 ? "red" : "green";
            item_info.pre_arrow = (target_1 - count) > 0 ? "down" : "up";
            item_info['comparison'] = true;
            var target_deviation = (target_1 - count) > 0 ? Math.round(((target_1 - count) / target_1) * 100) : Math.round((Math.abs((target_1 - count)) / target_1) * 100);
            if (target_deviation !== Infinity) item_info.target_deviation = field_utils.format.integer(target_deviation) + "%";
            else {
                item_info.target_deviation = target_deviation;
                item_info.pre_arrow = false;
            }
            var target_progress_deviation = target_1 == 0 ? 0 : Math.round((count / target_1) * 100);
            item_info.target_progress_deviation = field_utils.format.integer(target_progress_deviation) + "%";
            $kpi_preview = $(QWeb.render("kpi_template_2", item_info));
            $kpi_preview.find('.target_deviation').css({
                "color": color
            });
            if (field.target_view === "Progress Bar") {
                $kpi_preview.find('#progressbar').val(target_progress_deviation)
            }

            return $kpi_preview;
        },

        Percentage: function(count_1, count_2, field, item_info, target_1, $kpi_preview, kpi_data) {
            var count = parseInt((count_1 / count_2) * 100);
            item_info['count'] = count ? field_utils.format.integer(count) + "%" : "0%";
            item_info['count_tooltip'] = count ? count + "%" : "0%";
            item_info.target_progress_deviation = item_info['count']
            target_1 = target_1 > 100 ? 100 : target_1;
            item_info.target = target_1 + "%";
            item_info.pre_arrow = (target_1 - count) > 0 ? "down" : "up";
            var color = (target_1 - count) > 0 ? "red" : "green";
            item_info['target_enable'] = field.is_goal_enable;
            item_info['comparison'] = false;
            item_info.target_deviation = item_info.target > 100 ? 100 : item_info.target;
            $kpi_preview = $(QWeb.render("kpi_template_2", item_info));
            $kpi_preview.find('.target_deviation').css({
                "color": color
            });
            if (field.target_view === "Progress Bar") {
                if (count) $kpi_preview.find('#progressbar').val(count);
                else $kpi_preview.find('#progressbar').val(0);
            }

            return $kpi_preview;
        },

        KPIRender: function(item, grid) {
            var self = this;
            var field = item;
            var date_domain_fields = field.date_domain_fields;
            if (field.date_domain_fields === "none") date_domain_fields = self.dashboard_data.date_domain_fields;
            var valid_date_selection = ['last_day', 'this_week', 'this_month', 'this_quarter', 'this_year'];
            var kpi_data = JSON.parse(field.kpi_data);
            var count_1 = kpi_data[0].record_data;
            var count_2 = kpi_data[1] ? kpi_data[1].record_data : undefined;
            var target_1 = kpi_data[0].target;
            var target_view = field.target_view,
                pre_view = field.prev_view;
            var rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color);
            var dark_border_color_kpi = GlobalFunction.convert_to_rgba_function(self.dark_color_generator(field.background_color.split(',')[0], field.background_color.split(',')[1], -10));
            var dark_border_color_kpi_1 = "1px solid " + dark_border_color_kpi + ";";
            var font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color)
            if (field.is_goal_enable) {
                var diffrence = 0.0
                diffrence = count_1 - target_1
                var acheive = diffrence >= 0 ? true : false;
                diffrence = Math.abs(diffrence);
                var deviation = Math.round((diffrence / target_1) * 100)
                if (deviation !== Infinity) deviation = deviation ? field_utils.format.integer(deviation) + '%' : 0 + '%';
            }
            if (field.previous_data_field && valid_date_selection.indexOf(date_domain_fields) >= 0) {
                var previous_period_data = kpi_data[0].previous_data_field;
                var pre_diffrence = (count_1 - previous_period_data);
                var pre_acheive = pre_diffrence > 0 ? true : false;
                pre_diffrence = Math.abs(pre_diffrence);
                var pre_deviation = previous_period_data ? field_utils.format.integer(parseInt((pre_diffrence / previous_period_data) * 100)) + '%' : "100%"
            }
            item['IsDashboardManager'] = self.dashboard_data.dashboard_manager;
            var icon_url;
            if (field.selection_icon_field == "Custom") {
                if (field.icon[0]) {
                    icon_url = 'data:image/' + (self.file_type_word[field.icon[0]] || 'png') + ';base64,' + field.icon;
                } else {
                    icon_url = false;
                }
            }
            var rgba_icon_color = GlobalFunction.convert_to_rgba_function(field.default_icon_color)
            var item_info = {
                item: item,
                id: field.id,
                count_1: GlobalFunction.number_shorthand_function(kpi_data[0]['record_data'], 1),
                count_1_tooltip: kpi_data[0]['record_data'],
                count_2: kpi_data[1] ? String(kpi_data[1]['record_data']) : false,
                name: field.name ? field.name : field.model_id.data.display_name,
                target_progress_deviation: Math.round((count_1 / target_1) * 100) ? String(field_utils.format.integer(Math.round((count_1 / target_1) * 100))) : "0",
                selection_icon_field: field.selection_icon_field,
                default_icon: field.default_icon,
                icon_color: rgba_icon_color,
                target_deviation: deviation,
                target_arrow: acheive ? 'up' : 'down',
                enable_goal: field.is_goal_enable,
                previous_data_field: valid_date_selection.indexOf(date_domain_fields) >= 0 ? field.previous_data_field : false,
                target: GlobalFunction.number_shorthand_function(target_1, 1),
                previous_period_data: previous_period_data,
                pre_deviation: pre_deviation,
                pre_arrow: pre_acheive ? 'up' : 'down',
                target_view: field.target_view,
                pre_view: field.prev_view,
                dashboard_list: self.dashboard_data.dashboard_list,
                icon_url: icon_url,
                font_color:font_color_rgba_format,
                dark_border_color_kpi_1 : dark_border_color_kpi_1,
                date_selection_data: self.date_specific_filter_selections,
                date_selection_order: self.date_specific_filter_selection_order
            }

            if (item_info.target_deviation === Infinity) item_info.target_arrow = false;

            var $kpi_preview;
            if (!kpi_data[1]) {
                if (field.target_view === "Number" || !field.is_goal_enable) {
                    $kpi_preview = $(QWeb.render("kpi_template", item_info));
                } else if (field.target_view === "Progress Bar" && field.is_goal_enable) {
                    $kpi_preview = $(QWeb.render("kpi_template_3", item_info));
                    $kpi_preview.find('#progressbar').val(parseInt(item_info.target_progress_deviation));

                }

                if (field.is_goal_enable) {
                    if (acheive) {
                        $kpi_preview.find(".target_deviation").css({
                            "color": "green",
                        });
                    } else {
                        $kpi_preview.find(".target_deviation").css({
                            "color": "red",
                        });
                    }
                }
                if (field.previous_data_field && String(previous_period_data) && valid_date_selection.indexOf(date_domain_fields) >= 0) {
                    if (pre_acheive) {
                        $kpi_preview.find(".pre_deviation").css({
                            "color": "green",
                        });
                    } else {
                        $kpi_preview.find(".pre_deviation").css({
                            "color": "red",
                        });
                    }
                }
                if ($kpi_preview.find('.target_previous').children().length !== 2) {
                    $kpi_preview.find('.target_previous').addClass('justify-content-center');
                }
            } else {
                switch (field.kpi_compare_field) {
                    case "None":
                        var count_tooltip = String(count_1) + "/" + String(count_2);
                        var count = String(GlobalFunction.number_shorthand_function(count_1, 1)) + "/" + String(GlobalFunction.number_shorthand_function(count_2, 1));
                        item_info['count'] = count;
                        item_info['count_tooltip'] = count_tooltip;
                        item_info['target_enable'] = false;
                        $kpi_preview = $(QWeb.render("kpi_template_2", item_info));
                        break;
                    case "Sum":
                        $kpi_preview = self.Sum(count_1, count_2, item_info, field, target_1, $kpi_preview, kpi_data);
                        break;
                    case "Percentage":
                        $kpi_preview = self.Percentage(count_1, count_2, field, item_info, target_1, $kpi_preview, kpi_data);
                        break;
                    case "Ratio":
                        var gcd = self.get_gcd(Math.round(count_1), Math.round(count_2));
                        item_info['count'] = (isNaN(count_1 / gcd) ? 0 : GlobalFunction.number_shorthand_function(count_1 / gcd, 1)) + ":" + (isNaN(count_2 / gcd) ? 0 : GlobalFunction.number_shorthand_function(count_2 / gcd, 1));
                        item_info['count_tooltip'] = (isNaN(count_1 / gcd) ? 0 : count_1 / gcd) + ":" + (isNaN(count_2 / gcd) ? 0 : count_2 / gcd);
                        item_info['target_enable'] = false;
                        $kpi_preview = $(QWeb.render("kpi_template_2", item_info));
                        break;
                }
            }
            $kpi_preview.find('.dashboarditem_id').css({
                "background-color": rgba_background_color,
                "color": font_color_rgba_format,
                "border": dark_border_color_kpi_1
            });
            return $kpi_preview

        },
        ChartRender: function($gridstack_container, item) {
            var self = this;
            var chart_data = JSON.parse(item.chart_data);
            var isDrill = item.isDrill ? item.isDrill : false;
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.type_of_element.split('_')[0];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;

            }
            $gridstack_container.find('.chart_theme').data({
                chartType: chart_type,
                chartFamily: chart_family
            }); {
                chartType: "pie"
            }
            var $ChartContainer = $('<canvas id="chart_canvas_id" data-chart-id=' + chart_id + '/>');
            $gridstack_container.find('.card-body').append($ChartContainer);
            if (!item.show_records) {
                $gridstack_container.find('.dashboard_item_chart_info').hide();
            }
            item.$el = $gridstack_container;
            if (chart_family === "circle") {
                if (chart_data && chart_data['labels'].length > 30) {
                    $gridstack_container.find(".dashboard_color_option").remove();
                    $gridstack_container.find(".card-body").empty().append($("<div style='font-size:20px;'>Too many records for selected Chart Type. Consider using <strong>Domain</strong> to filter records or <strong>Record Limit</strong> to limit the no of records under <strong>30.</strong>"));
                    return;
                }
            }

            if (chart_data["show_second_y_scale"] && item.type_of_element === 'bar_chart') {
                var scales = {}
                scales.yAxes = [{
                        type: "linear",
                        display: true,
                        position: "left",
                        id: "y-axis-0",
                        gridLines: {
                            display: true
                        },
                        labels: {
                            show: true,
                        }
                    },
                    {
                        type: "linear",
                        display: true,
                        position: "right",
                        id: "y-axis-1",
                        labels: {
                            show: true,
                        },
                        ticks: {
                            beginAtZero: true,
                            callback: function(value, index, values) {
                                var selection = chart_data.selection;
                                if (selection === 'monetary') {
                                    var currency_id = chart_data.currency;
                                    var data = GlobalFunction.number_shorthand_function(value, 1);
                                    data = GlobalFunction.currency_monetary_function(data, currency_id);
                                    return data;
                                } else if (selection === 'custom') {
                                    var field = chart_data.field;
                                    return GlobalFunction.number_shorthand_function(value, 1) + ' ' + field;
                                } else {
                                    return GlobalFunction.number_shorthand_function(value, 1);
                                }
                            },
                        }
                    }
                ]
            }
            var chart_plugin = [];
//            if (item.show_data_value) {
                chart_plugin.push(ChartDataLabels);
//            }
            var MyChart = new Chart($ChartContainer[0], {
                type: chart_type === "area" ? "line" : chart_type,
                plugins: chart_plugin,
                data: {
                    labels: chart_data['labels'],
                    groupByIds: chart_data['groupByIds'],
                    domains: chart_data['domains'],
                    datasets: chart_data.datasets,
                },
                options: {
                    maintainAspectRatio: false,
                    responsiveAnimationDuration: 1000,
                    animation: {
                        easing: 'easeInQuad',
                    },
                    scales: scales,
                    layout: {
                        padding: {
                            bottom: 0,
                        }
                    },
                    plugins: {
                        datalabels: {
                            backgroundColor: function(context) {
                                return context.dataset.backgroundColor;
                            },
                            borderRadius: 4,
                            color: 'white',
                            font: {
                                weight: 'bold'
                            },
                            anchor: 'center',
                            display: 'auto',
                            clamp: true,
                            formatter: function(value, ctx) {
                                let sum = 0;
                                let dataArr = ctx.dataset.data;
                                dataArr.map(data => {
                                    sum += data;
                                });
                                let percentage = sum === 0 ? 0 + "%" : (value * 100 / sum).toFixed(2) + "%";
                                return percentage;
                            },
                        },
                    },

                }
            });

            this.chart_container[chart_id] = MyChart;
            if (chart_data && chart_data["datasets"].length > 0) self.ChartColors(item.chart_theme_selection, MyChart, chart_type, chart_family, item.bar_chart_stacked, item.semi_circle_chart, item.show_data_value, chart_data, item);

        },
        get_gcd: function(a, b) {
            return (b == 0) ? a : this.get_gcd(b, a % b);
        },

        _onInputChange: function(e) {
            this.NewDashboardName = e.target.value
        },

        DuplicateElement: function(e) {
            var self = this;
            var element_id = $($(e.target).parentsUntil(".dashboarditem_id").slice(-1)[0]).parent().attr('id');
            var dashboard_id = $($(e.target).parentsUntil(".dashboarditem_id").slice(-1)[0]).find('.dashboard_select').val();
            var dashboard_name = $($(e.target).parentsUntil(".dashboarditem_id").slice(-1)[0]).find('.dashboard_select option:selected').text();
            this._rpc({
                model: 'dashboard_pro.element',
                method: 'copy',
                args: [parseInt(element_id), {
                    'dashboard_pro_dashboard_id': parseInt(dashboard_id)
                }],
            }).then(function(result) {
                self.action_manager.notifications.add(
                    _t('Selected item is duplicated to ' + dashboard_name + ' .'),{
                        type: 'warning',
                        title: _t("Item Duplicated")
                });
                $.when(self.fetch_data()).then(function() {
                    self.remove_time_diff();
                    self.MainDashboardRender();
                    self.update_time_diff();
                });
            })
        },
        MoveElement: function(e) {
            var self = this;
            var element_id = $($(e.target).parentsUntil(".dashboarditem_id").slice(-1)[0]).parent().attr('id');
            var dashboard_id = $($(e.target).parentsUntil(".dashboarditem_id").slice(-1)[0]).find('.dashboard_select').val();
            var dashboard_name = $($(e.target).parentsUntil(".dashboarditem_id").slice(-1)[0]).find('.dashboard_select option:selected').text();
            this._rpc({
                model: 'dashboard_pro.element',
                method: 'write',
                args: [parseInt(element_id), {
                    'dashboard_pro_dashboard_id': parseInt(dashboard_id)
                }],
            }).then(function(result) {
                self.action_manager.notifications.add(
                     _t('Selected item is moved to ' + dashboard_name + ' .'),{
                        type: 'warning',
                        title: _t("Item Moved")
                });
                $.when(self.fetch_data()).then(function() {
                    self.remove_time_diff();
                    self.MainDashboardRender();
                    self.update_time_diff();
                });
            });
        },

        _GetDateValues: function() {
            var self = this;

            var date_filter_selected = self.dashboard_data.date_domain_fields;
            self.$el.find('#' + date_filter_selected).addClass("date_filter_selected");
            self.$el.find('#date_domain_fields').text(self.date_filter_selections[date_filter_selected]);

            if (self.dashboard_data.date_domain_fields === 'last_custom') {
                self.$el.find('.date_input_fields').removeClass("hide");
                self.$el.find('.date_filter_dropdown').addClass("btn_first_child_radius");
            } else if (self.dashboard_data.date_domain_fields !== 'last_custom') {
                self.$el.find('.date_input_fields').addClass("hide");
            }
        },

        _onClearDateValues: function() {
            var self = this;

            self.DateFilterSelection = 'none';
            self.DateFilterStartDate = false;
            self.DateFilterEndDate = false;

            $.when(self.fetch_data()).then(function() {
                self.MainDashboardRender();
            });
        },


        _renderDateFilterDatePicker: function() {
            var self = this;
            self.$el.find(".dashboard_link").removeClass("hide");
            var startDate = self.dashboard_data.starting_date_dashboard ? moment.utc(self.dashboard_data.starting_date_dashboard).local() : moment();
            var endDate = self.dashboard_data.ending_date_dashboard ? moment.utc(self.dashboard_data.ending_date_dashboard).local() : moment();

            this.StartDatePickerWidget = new(datepicker.DateTimeWidget)(this);

            this.StartDatePickerWidget.appendTo(self.$el.find(".date_input_fields")).then((function() {
                this.StartDatePickerWidget.$el.addClass("btn_middle_child o_input");
                this.StartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
                this.StartDatePickerWidget.setValue(startDate);
                this.StartDatePickerWidget.on("datetime_changed", this, function() {
                    self.$el.find(".apply-dashboard-date-filter").removeClass("hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("hide");
                });
            }).bind(this));

            this.EndDatePickerWidget = new(datepicker.DateTimeWidget)(this);
            this.EndDatePickerWidget.appendTo(self.$el.find(".date_input_fields")).then((function() {
                this.EndDatePickerWidget.$el.addClass("btn_last_child o_input");
                this.StartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
                this.EndDatePickerWidget.setValue(endDate);
                this.EndDatePickerWidget.on("datetime_changed", this, function() {
                    self.$el.find(".apply-dashboard-date-filter").removeClass("hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("hide");
                });
            }).bind(this));

            self._GetDateValues();
        },
        _renderSpecificDateFilterDatePicker: function() {
            var self = this;
            self.$el.find(".dashboard_link").removeClass("hide");
            var startDate = self.dashboard_data.starting_date_dashboard ? moment.utc(self.dashboard_data.starting_date_dashboard).local() : moment();
            var endDate = self.dashboard_data.ending_date_dashboard ? moment.utc(self.dashboard_data.ending_date_dashboard).local() : moment();

            this.SpecificStartDatePickerWidget = new(datepicker.DateTimeWidget)(this);

            this.SpecificStartDatePickerWidget.appendTo(self.$el.find(".date_input_fields_specific_element")).then((function() {
                this.SpecificStartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
                this.SpecificStartDatePickerWidget.setValue(startDate);
                this.SpecificStartDatePickerWidget.on("datetime_changed", this, function() {
                    self.$el.find(".apply-specific-dashboard-date-filter").removeClass("hide");
                    self.$el.find(".clear-specific-dashboard-date-filter").removeClass("hide");
                });
            }).bind(this));

            this.SpecificEndDatePickerWidget = new(datepicker.DateTimeWidget)(this);
            this.SpecificEndDatePickerWidget.appendTo(self.$el.find(".date_input_fields_specific_element")).then((function() {
                this.SpecificStartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
                this.SpecificEndDatePickerWidget.setValue(endDate);
                this.SpecificEndDatePickerWidget.on("datetime_changed", this, function() {
                    self.$el.find(".apply-specific-dashboard-date-filter").removeClass("hide");
                    self.$el.find(".clear-specific-dashboard-date-filter").removeClass("hide");
                });
            }).bind(this));

            self._GetDateValues();
        },

        _onApplyDateFilter: function(e) {
            var self = this;
            time
            var start_date = self.StartDatePickerWidget.getValue();
            var end_date = self.EndDatePickerWidget.getValue();
            if (start_date === "Invalid date") {
                alert("Invalid Date is given in Start Date.")
            } else if (end_date === "Invalid date") {
                alert("Invalid Date is given in End Date.")
            } else if (self.$el.find('.date_filter_selected').attr('id') !== "last_custom") {
                self.DateFilterSelection = self.$el.find('.date_filter_selected').attr('id');

                $.when(self.fetch_data()).then(function() {
                    self.DashboardElementUpdate(Object.keys(self.dashboard_data.element_data));
                });
            } else {
                if (start_date && end_date) {
                    if (start_date <= end_date) {

                        self.DateFilterSelection = self.$el.find('.date_filter_selected').attr('id');
                        self.DateFilterStartDate = start_date.add(-this.getSession().getTZOffset(start_date), 'minutes');
                        self.DateFilterEndDate = end_date.add(-this.getSession().getTZOffset(start_date), 'minutes');

                        $.when(self.fetch_data()).then(function() {
                            self.MainDashboardRender();
                        });

                    } else {
                        alert(_t("Start date should be less than end date"));
                    }
                } else {
                    alert(_t("Please enter start date and end date"));
                }
            }
        },
        _onApplySpecificDateFilter: function(e) {
            var self = this;
            time

            var start_date = self.SpecificStartDatePickerWidget.getValue();
            var end_date = self.SpecificEndDatePickerWidget.getValue();
            if (start_date === "Invalid date") {
                alert("Invalid Date is given in Start Date.")
            } else if (end_date === "Invalid date") {
                alert("Invalid Date is given in End Date.")
            } else if (self.$el.find('.date_filter_selected').attr('id') !== "last_custom") {
                self.DateFilterSelection = self.$el.find('.date_filter_selected').attr('id');
                self.date_specific_container_id = e.id;
                $.when(self.fetch_data()).then(function() {
                    var obj = {};
                    var id = self.date_specific_container_id;
                    var data_new = self.dashboard_data.element_data[id];
                    obj[id] = data_new;
                    self.DashboardElementUpdate(Object.keys(obj));
                });
            } else {
                if (start_date && end_date) {
                    if (start_date <= end_date) {

                        self.DateFilterSelection = self.$el.find('.date_filter_selected').attr('id');
                        self.DateFilterStartDate = start_date.add(-this.getSession().getTZOffset(start_date), 'minutes');
                        self.DateFilterEndDate = end_date.add(-this.getSession().getTZOffset(start_date), 'minutes');

                        $.when(self.fetch_data()).then(function() {
                            self.MainDashboardRender();
                            var obj = {};
                            var id = self.date_specific_container_id;
                            var data_new = self.dashboard_data.element_data[id];
                            obj[id] = data_new;
                            self.DashboardElementUpdate(Object.keys(obj));
                        });

                    } else {
                        alert(_t("Start date should be less than end date"));
                    }
                } else {
                    alert(_t("Please enter start date and end date"));
                }
            }
        },

        _OnDateFilterMenuSelect: function(e) {
            if (e.target.id !== 'date_selector_container') {
                var self = this;
                _.each($('.date_filter_selected'), function($filter_options) {
                    $($filter_options).removeClass("date_filter_selected")
                });
                $(e.target.parentElement).addClass("date_filter_selected");
                $('#date_domain_fields').text(self.date_filter_selections[e.target.parentElement.id]);

                if (e.target.parentElement.id !== "last_custom") {
                    $('.date_input_fields').addClass("hide");
                    $('.date_filter_dropdown').removeClass("btn_first_child_radius");
                    e.target.parentElement.id === "none" ? self._onClearDateValues() : self._onApplyDateFilter();
                } else if (e.target.parentElement.id === "last_custom") {
                    $("#start_date_picker").val(null).removeClass("hide");
                    $("#end_date_picker").val(null).removeClass("hide");
                    $('.date_input_fields').removeClass("hide");
                    $('.date_filter_dropdown').addClass("btn_first_child_radius");
                    self.$el.find(".apply-dashboard-date-filter").removeClass("hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("hide");
                    self.$el.find(".dashboard_top_settings").addClass("hide");
                    self.$el.find(".theme_group").addClass("hide");
                }
            }
        },
        _OnDateSpecificFilterMenuSelect: function(e) {
            if (e.target.id !== 'date_specific_filters_menu') {
                var self = this;
                _.each($('.date_filter_selected'), function($filter_options) {
                    $($filter_options).removeClass("date_filter_selected")
                });
                $(e.target.parentElement).addClass("date_filter_selected");
                $('#date_domain_fields').text(self.date_filter_selections[e.target.parentElement.id]);

                if (e.target.parentElement.id !== "last_custom") {
                    var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'));
                    $('.date_input_fields_specific_element').addClass("hide");
                    $('.date_filter_dropdown').removeClass("btn_first_child_radius");
                    e.target.parentElement.id === "none" ? self._onClearDateValues() : self._onApplySpecificDateFilter({id : id});
                } else if (e.target.parentElement.id === "last_custom") {
                    var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'));
                    this.date_specific_container_id = id;
                    $("#start_specific_date_picker").val(null).removeClass("hide");
                    $("#end_specific_date_picker").val(null).removeClass("hide");
                    $('.date_input_fields_specific_element').removeClass("hide");
                    $('.date_filter_dropdown').addClass("btn_first_child_radius");
                    self.$el.find(".date_specific_apply_clear_print").removeClass("hide");
                    self.$el.find(".apply-specific-dashboard-date-filter").removeClass("hide");
                    self.$el.find(".clear-specific-dashboard-date-filter").removeClass("hide");
                }
            }
        },

        ChartExportXlsCsv: function(e) {
            var chart_id = e.currentTarget.dataset.chartId;
            var name = this.dashboard_data.element_data[chart_id].name;
            var data = {
                "header": name,
                "chart_data": this.dashboard_data.element_data[chart_id].chart_data,
            }
            framework.blockUI();
            this.getSession().get_file({
                url: '/dashboard_pro/export/' + e.currentTarget.dataset.format,
                data: {
                    data: JSON.stringify(data)
                },
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
        },

        ChartExportPdf: function(e) {
            var chart_id = e.currentTarget.dataset.chartId;
            var name = this.dashboard_data.element_data[chart_id].name;
            var base64_image = this.chart_container[chart_id].toBase64Image()
            var doc = new jsPDF('p', 'mm');
            doc.addImage(base64_image, 'PNG', 5, 10, 200, 0);
            doc.save(name);
        },

        ItemExportJson: function(e) {
            var itemId = $(e.target).parents('.dashboard_element_buttons_container')[0].dataset.element_id;
            var name = this.dashboard_data.element_data[itemId].name;
            var data = {
                'header': name,
                element_id: itemId,
            }
            framework.blockUI();
            this.getSession().get_file({
                url: '/dashboard_pro/export/item_json',
                data: {
                    data: JSON.stringify(data)
                },
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
            e.stopPropagation();
        },

        LoadMoreRecords: function(e) {
            var self = this;
            var intial_count = e.target.parentElement.dataset.prevOffset;
            var offset = e.target.parentElement.dataset.next_offset;
            var itemId = e.currentTarget.dataset.itemId;

            if (itemId in self.UpdateDashboard) {
                clearInterval(self.UpdateDashboard[itemId])
                delete self.UpdateDashboard[itemId];
            }

            this._rpc({
                model: 'dashboard_pro.main_dashboard',
                method: 'list_data_offset',
                context: self.getContext(),
                args: [parseInt(itemId), {
                    intial_count: intial_count,
                    offset: offset,
                    }, parseInt(self.dashboard_id)],
            }).then(function(result) {
                var element_data = self.dashboard_data.element_data[itemId];
                self.dashboard_data.element_data[itemId]['json_list_data'] = result.json_list_data;
                var item_view = self.$el.find(".grid-stack-item[data-gs-id=" + element_data.id + "]");
                item_view.find('.card-body').empty();
                item_view.find('.card-body').append(self.renderListViewData(element_data));
                $(e.currentTarget).parents('.pager').find('.value').text(result.offset + "-" + result.next_offset);
                e.target.parentElement.dataset.next_offset = result.next_offset;
                e.target.parentElement.dataset.prevOffset = result.offset;
                $(e.currentTarget.parentElement).find('.load_previous').removeClass('event_offer_list');
                if (result.next_offset < parseInt(result.offset) + 14 || result.next_offset == element_data.data_calculation_value || result.next_offset === result.limit){
                    $(e.currentTarget).addClass('event_offer_list');
                }
            });
        },
        _renderGraph: function(item) {
            var self = this;
            var chart_data = JSON.parse(item.chart_data);
            var isDrill = item.isDrill ? item.isDrill : false;
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.type_of_element.split('_')[0];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;

            }

            var $gridstack_container = $(QWeb.render('gridstack_container', {
                chart_title: chart_title,
                IsDashboardManager: self.dashboard_data.dashboard_manager,
                dashboard_list: self.dashboard_data.dashboard_list,
                chart_id: chart_id,
                chart_family: chart_family,
                chart_type: chart_type,
                ChartColorOptions: this.ChartColorOptions,
                date_selection_data: self.date_specific_filter_selections,
                date_selection_order: self.date_specific_filter_selection_order
            })).addClass('dashboarditem_id');
            if(!this.fullScreenOverlay){
                $gridstack_container.find('.li_' + item.chart_theme_selection).addClass('date_filter_selected');
                if (chart_id in self.gridstackConfig) {
                    self.grid.addWidget($gridstack_container, self.gridstackConfig[chart_id].x, self.gridstackConfig[chart_id].y, self.gridstackConfig[chart_id].width, self.gridstackConfig[chart_id].height, false, 11, null, 3, null, chart_id);
                } else {
                    self.grid.addWidget($gridstack_container, 0, 0, 13, 4, true, 11, null, 3, null, chart_id);
                }
            }else{
                this.$el.find('.full_screen_overlay').append($gridstack_container);
            }
            self.ChartRender($gridstack_container, item);
        },

        LoadPreviousRecords: function(e) {
            var self = this;
            var offset = parseInt(e.target.parentElement.dataset.prevOffset) - 16;
            var intial_count = e.target.parentElement.dataset.next_offset;
            var itemId = e.currentTarget.dataset.itemId;
            if (offset <= 0) {
                var updateValue = self.dashboard_data.element_data[itemId]["update_element_data_time"];
                if (updateValue) {
                    var updateinterval = setInterval(function() {
                        self.GetUpdateElement(itemId)
                    }, updateValue);
                    self.UpdateDashboard[itemId] = updateinterval;
                }
            }
            this._rpc({
                model: 'dashboard_pro.main_dashboard',
                method: 'list_data_offset',
                context: self.getContext(),
                args: [parseInt(itemId), {
                    intial_count: intial_count,
                    offset: offset,
                    }, parseInt(self.dashboard_id)],
            }).then(function(result) {
                var element_data = self.dashboard_data.element_data[itemId];
                self.dashboard_data.element_data[itemId]['json_list_data'] = result.json_list_data;
                var item_view = self.$el.find(".grid-stack-item[data-gs-id=" + element_data.id + "]");
                item_view.find('.card-body').empty();
                item_view.find('.card-body').append(self.renderListViewData(element_data));
                $(e.currentTarget).parents('.pager').find('.value').text(result.offset + "-" + result.next_offset);
                e.target.parentElement.dataset.next_offset = result.next_offset;
                e.target.parentElement.dataset.prevOffset = result.offset;
                $(e.currentTarget.parentElement).find('.load_next').removeClass('event_offer_list');
                if (result.offset === 1) {
                    $(e.currentTarget).addClass('event_offer_list');
                }
            });
        },

    });

    core.action_registry.add('openeducat_dashboard_kpi', DashboardPro);

    return DashboardPro;
});
