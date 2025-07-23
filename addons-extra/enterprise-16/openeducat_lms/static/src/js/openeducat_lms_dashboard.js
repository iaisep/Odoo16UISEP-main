odoo.define('openeducat_lms.openeducat_lms_dashboard', function(require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var AbstractAction = require('web.AbstractAction');

    var _t = core._t;
    var QWeb = core.qweb;


    var LmsDashboard = AbstractAction.extend({
        template: "OpenEduCatLMSDashboard",
        cssLibs: [
            '/web/static/lib/nvd3/nv.d3.css'
        ],
        jsLibs: [
            '/web/static/lib/nvd3/d3.v3.js',
            '/web/static/lib/nvd3/nv.d3.js',
            '/web/static/src/js/libs/nvd3.js'
        ],

        init: function(parent, context) {
           this._super(parent);
        },

        willStart: function() {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super());
        },

        start: function() {
            var self = this;
            self.render_lms_dashboard();
            return this._super.apply(this, arguments);
        },

        render_lms_dashboard: function() {
            var self = this;

            self._rpc({route: '/openeducat_lms/fetch_course', params: {}}).done
            (function(result) {
                self.$el.html(QWeb.render('OpenEduCatLMSDashboard', {
                    course_ids: result.course_ids
                }));

                self._rpc({route: '/openeducat_lms/compute_openeducat_graph',
                params: {},}).done
                (function(result) {
                    load_chart_bar('#total_enrollment_stat_chart_div', result);
                    self.$('#total_enrollment_stat_chart_div div.o_loader').hide();
                });

                self.render_course_dashboard_data();
                $('#course_selection').on('change', function() {
                    self.render_course_dashboard_data();
                });
            });

        },

        render_course_dashboard_data: function() {
            addLoader(this.$('#course_enrollment_stat_chart_div'));
            var self = this;
            var sel = document.getElementById('course_selection');
            self._rpc({route: '/openeducat_lms/get_lms_dash_data', params: {
                course_id: sel.value
            }}).done(function(result) {
                var enrolled_users = document.getElementById('enrolled_users');
                if (enrolled_users) {
                    enrolled_users.innerHTML = '<h1>' + result.enrolled_users + '</h1>';
                }

                var days_since_launch = document.getElementById('days_since_launch');
                if (days_since_launch) {
                    days_since_launch.innerHTML = '<h2>' + result.days_since_launch + '</h2>';
                }

                var course_duration = document.getElementById("course_duration");
                if (course_duration) {
                    course_duration.innerHTML = '<h2>' + result.course_duration + '</h2>';
                }

                var training_material = document.getElementById('training_material');
                if (training_material) {
                    training_material.innerHTML = '<h2>' + result.training_material + '</h2>';
                }

                var course_to_begin = document.getElementById('course_to_begin');
                if (course_to_begin) {
                    course_to_begin.innerHTML = '<h2>' + result.course_to_begin + '</h2>';
                }

                var course_in_progress = document.getElementById('course_in_progress');
                if (course_in_progress) {
                    course_in_progress.innerHTML = '<h2>' + result.course_in_progress + '</h2>';
                }

                var course_completed = document.getElementById('course_completed');
                if (course_completed) {
                    course_completed.innerHTML = '<h2>' + result.course_completed + '</h2>';
                }
            });

            self._rpc({route: '/openeducat_lms/compute_openeducat_course_graph',
             params:{
                course_id: sel.value
            }}).done(function(result) {
                load_chart_bar('#course_enrollment_stat_chart_div', result);
                self.$('#course_enrollment_stat_chart_div div.o_loader').hide();
            });
        },
    });

    // Load Bar Chart Function
    function load_chart_bar(div_to_display, result) {
        var data_chart = [{
            key: _t("OpenEduCat"),
            values: result
        }];

        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function(d) {
                    return d.label;
                })
                .y(function(d) {
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

    core.action_registry.add('openeducat_lms_dashboard', LmsDashboard);

    return LmsDashboard;

});
