odoo.define('openeducat_core_enterprise.enterprise_main_dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var AbstractAction = require('web.AbstractAction');

    var _t = core._t;
    var QWeb = core.qweb;


    var MyMainDashboard = AbstractAction.extend({
        template: "OpenEduCatMainDashboard",
        cssLibs: [
            '/web/static/lib/nvd3/nv.d3.css'
        ],
        jsLibs: [
            '/web/static/lib/nvd3/d3.v3.js',
            '/web/static/lib/nvd3/nv.d3.js',
            '/web/static/src/js/libs/nvd3.js'
        ],

        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
            });
        },

        init: function (parent, context) {
            this._super(parent);
        },

        events: {
            'click .enrolled_student': 'on_enrolled_student_clicked',
            'click .today_lecture': 'on_today_lecture_clicked',
            'click .total_assignment': 'on_total_assignment_clicked',
        },

        start: function () {
            var self = this;
            self.render_batch_dashboard();
            return this._super.apply(this, arguments);
        },

        render_batch_dashboard: function () {
            var self = this;

            self._rpc({
                route: '/openeducat_core_enterprise/get_main_dash_data',
                params: {},
            }).done(function (result) {
                var student_enroll_rate = document.getElementById("student_enroll_rate");
                if (student_enroll_rate) {
                    student_enroll_rate.innerHTML = "<h2>" + result.student_enroll_rate + ' %</h2>';
                }
                var erolled_students = document.getElementById("erolled_students");
                if (erolled_students) {
                    erolled_students.innerHTML = "<h2>" + result.erolled_students + '</h2>';
                }
                var mf_ratio = document.getElementById("mf_ratio");
                if (mf_ratio) {
                    mf_ratio.innerHTML = "<h2>" + result.mf_ratio + '</h2>';
                }
                var sp_ratio = document.getElementById("sp_ratio");
                if (sp_ratio) {
                    sp_ratio.innerHTML = "<h2>" + result.sp_ratio + '</h2>';
                }
            });

            self._rpc({
                route: '/openeducat_core_enterprise/fetch_batch',
                params: {},
            }).done(function (result) {
                self.$el.html(QWeb.render("OpenEduCatMainDashboard", {
                    batch_ids: result.batch_ids
                }));
                self.render_batch_dashboard_graph();
                $('#batch_selection').on('change', function () {
                    self.render_batch_dashboard_graph();
                });
            });
        },

        render_batch_dashboard_graph: function () {
            addLoader(this.$('#stat_chart_div'));
            var self = this;
            var sel = document.getElementById('batch_selection');
            self._rpc({
                route: '/openeducat_core_enterprise/compute_openeducat_batch_graph',
                params: {
                    batch_id: sel.value
                }
            }).done(function (result) {
                load_chart_bar('#stat_chart_div', result);
                self.$('#stat_chart_div div.o_loader').hide();
            });
            self._rpc({
                route: '/openeducat_core_enterprise/get_batch_dashboard_data',
                params: {
                    batch_id: sel.value
                }
            }).done(function (result) {
                var tar = document.getElementById("tar");
                if (tar) {
                    tar.innerHTML = "<h2>" + result.tar + '</h2>';
                }
                ;
                var ts = document.getElementById("ts");
                if (ts) {
                    ts.innerHTML = "<h2>" + result.ts + '</h2>';
                }
                ;
                var tbl = document.getElementById("tbl");
                if (tbl) {
                    tbl.innerHTML = "<h2>" + result.tbl + '</h2>';
                }
                ;
                var ta = document.getElementById("ta");
                if (ta) {
                    ta.innerHTML = "<h2>" + result.ta + '</h2>';
                }
                ;
            });
        },

        on_enrolled_student_clicked: function (ev) {
            var context = {};
            var self = this;
            context.search_default_enrolled_student = 1;
            return self._rpc({
                route: "/web/action/load",
                params: {
                    action_id: "openeducat_admission.act_open_op_admission_view"
                }
            }).done(function (result) {
                if (result) {
                    result.views = [
                        [false, 'list'],
                        [false, 'form']
                    ];
                    result.context = context;
                    return self.do_action(result);
                };
            })
        },

        on_today_lecture_clicked: function (ev) {
            var context = {};
            var self = this;
            var sel = document.getElementById('batch_selection');
            context.active_id = [parseInt(sel.value)];
            return self._rpc({
                route: "/web/action/load",
                params: {
                    action_id: "openeducat_timetable_enterprise.act_main_dashboard_op_timetable_view", context: context
                }
            }).done(function (result) {
                if (result) {
                    result.views = [
                        [false, 'list'],
                        [false, 'form']
                    ];
                    result.context = context;
                    return self.do_action(result);
                };
            })
        },

        on_total_assignment_clicked: function (ev) {
            var context = {};
            var self = this;
            var sel = document.getElementById('batch_selection');
            context.search_default_batch_id = [parseInt(sel.value)];
            return self._rpc({
                route: "/web/action/load",
                params: {
                    action_id: "openeducat_assignment.act_open_op_assignment_view"
                }
            }).done(function (result) {
                if (result) {
                    result.views = [
                        [false, 'list'],
                        [false, 'form']
                    ];
                    result.context = context;
                    return self.do_action(result);
                }
                ;
            })
        },
    });

    // Load Bar Chart Function
    function load_chart_bar(div_to_display, result) {
        var data_chart = [{
            key: _t("OpenEduCat"),
            values: result
        }];
        nv.addGraph(function () {
            var chart = nv.models.discreteBarChart()
                .x(function (d) {
                    return d.label;
                })
                .y(function (d) {
                    return d.value;
                })
                .staggerLabels(true)
                .showValues(true)
                .duration(350);
            chart.tooltip.enabled(true);
            var svg = d3.select(div_to_display)
                .append("svg")
                .attr("height", '20em');
            svg
                .datum(data_chart)
                .call(chart);
            nv.utils.windowResize(chart.update);
            return chart;
        });
    }

    function addLoader(selector) {
        var loader = '<span class="fa fa-3x fa-spin fa-spinner fa-pulse"/>';
        selector.html("<div class='o_loader'>" + loader + "</div>");
    }

    core.action_registry.add('openeducat_main_dashboard', MyMainDashboard);

    return MyMainDashboard;

});
