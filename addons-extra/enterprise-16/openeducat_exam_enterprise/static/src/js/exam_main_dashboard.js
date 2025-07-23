odoo.define('openeducat_exam_enterprise.exam_main_dashboard', function(require) {
    "use strict";

    var core = require("web.core");
    var AbstractAction = require('web.AbstractAction');

    var QWeb = core.qweb;

    var ExamDashboard = AbstractAction.extend({
        start: function() {
            this._super.apply(this, arguments);
            this.render_dashboard();
        },

        events: {
            'click .card-green': 'show_all_exams',
            'click .card-blue': 'show_pending_exams',
            'click .card-orange': 'show_done_exams',
            'click .card-grey': 'show_exam_sessions',
        },

        show_view: function(model, context, caption) {
            var self = this,
                isEmpty = Object.keys(context).length === 0,
                domain = [];

            if(!isEmpty) {
                domain = [['state', '=', context.state]];
            }

             return this.do_action({
                name: caption,
                type: 'ir.actions.act_window',
                res_model: model,
                res_id: self.id,
                views: [[false, 'list'], [false, 'form']],
                domain: domain
            }, {
                on_reverse_breadcrumb: function() {
                    self.render_dashboard();
                },
            });
        },

        show_all_exams: function() {
            return this.show_view("op.exam", {}, "Exams");
        },

        show_pending_exams: function() {
            return this.show_view("op.exam", {'state': 'draft'}, "Exams");
        },

        show_done_exams: function() {
            return this.show_view("op.exam", {'state': 'done'}, "Exams");
        },

        show_exam_sessions: function() {
            return this.show_view("op.exam.session", {}, "Exam Sessions");
        },

        getRandomColor: function() {
            var letters = '0123456789ABCDEF';
            var color = '#';
            for (var i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        },

        render_line_chart: function(result) {
            var self = this,
                exam_names = [],
                ratios = [],
                chart = self.$el.find('#line_chart');

            _.each(result, function(exam) {
                exam_names.push(exam.name);
                ratios.push(exam.ratio.toFixed(2));
            });

            try {
                if(chart) {
                    Chart.defaults.global.defaultFontSize = 13;
                    Chart.defaults.global.defaultFontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif';
                    var ctx = chart[0].getContext('2d');
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: exam_names,
                            datasets: [{
                                label: "Pass Ratio (%)",
                                data: ratios,
                                fill: true,
                                backgroundColor: '#B0BEC5',
                                borderWidth: 1,
                                borderColor: '#3F51B5'
                            }]
                        },
                        options: {
                            responsive: true,
                            'animation': {
                                duration: 2000,
                            },
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        min: 50,
                                        max: 100,
                                        stepSize: 10,
                                    },
                                }],
                                xAxes: [{
                                    scaleLabel: {
                                        labelString: 'Exams',
                                        display: true,
                                    }
                                }]
                            },
                            legend: {
                                labels: {
                                    fontColor: 'black',
                                }
                            }
                        }
                    });
                }
            } catch (e) {
                console.error("Something went wrong...", e);
            }
        },

        render_pie_chart: function(result) {
            var self = this,
                exam_names = [],
                ratios = [],
                colors = [],
                chart = self.$el.find('#pie_chart');

            _.each(result, function(exam) {
                exam_names.push(exam.name);
                ratios.push(exam.ratio.toFixed(2));
                colors.push(self.getRandomColor());
            });

            try {
                if(chart) {
                    var ctx = chart[0].getContext('2d');
                    new Chart(ctx, {
                        type: 'pie',
                        data: {
                            datasets: [{
                                data: ratios,
                                backgroundColor: colors,
                            }],
                            labels: exam_names
                        },
                        options: {
                            responsive: true,
                            animation: {
                                duration: 2000,
                            }
                        }
                    });
                }
            } catch (e) {
                console.error("Something went wrong...", e);
            }
        },

        update_table_data: function(session_id) {
            var self = this;
            self._rpc({
                route: '/get_subject_details',
                params: { session_id: session_id }
            }).done(function(result) {
                var $table = self.$el.find('.table'),
                    $thead = $table.find('thead'),
                    $tbody = $('<tbody></tbody>');

                $table.empty();
                $thead.appendTo($table);

                _.each(result, function(data) {
                    var href = "web?=#id=" + data.id + "&view_type=form&model=op.exam";
                    var $tr = $('<tr></tr>'),
                        $td_exam = $('<td><a target="new "href=' + href + '>' + data.exam + '</a></td>'),
                        $td_code = $('<td>' + data.code + '</td>'),
                        $td_subject = $('<td>' + data.name + '</td>'),
                        $td_start_time = $('<td>' + data.start_time + '</td>'),
                        $td_end_time = $('<td>' + data.end_time + '</td>'),
                        $td_min_marks = $('<td>' + data.min_marks + '</td>'),
                        $td_total_marks = $('<td>' + data.total_marks + '</td>');

                    $td_exam.appendTo($tr);
                    $td_code.appendTo($tr);
                    $td_subject.appendTo($tr);
                    $td_start_time.appendTo($tr);
                    $td_end_time.appendTo($tr);
                    $td_min_marks.appendTo($tr);
                    $td_total_marks.appendTo($tr);
                    $tr.appendTo($tbody);
                });
                $tbody.appendTo($table);
            });
        },

        render_dashboard: function() {
            var self = this,
                total_exams = Object,
                done_exams = Object,
                pending_exams = Object,
                all_exams_sessions = Object;

            self._rpc({
                route: '/get_exam_sessions',
                params: {}
            }).done(function(result) {
                var $wrapper = self.$el.html(QWeb.render('ExamMainDashboard', {
                    session_ids: result.session_ids
                }));
                total_exams = $wrapper.find('#total_exams');
                done_exams = $wrapper.find('#done_exams');
                pending_exams = $wrapper.find('#pending_exams');
                all_exams_sessions = $wrapper.find('#exam_sessions');
                self.update_table_data(1);
                $wrapper.find('#session_id').on('change', function() {
                    self.update_table_data($(this).val());
                });
            });

            self._rpc({
                'route': '/get_exam_counts',
                'params': {}
            }).done(function(result) {
                if(result && total_exams.selector && done_exams.selector && pending_exams.selector && all_exams_sessions.selector) {
                    total_exams.text(result.all_exams);
                    done_exams.text(result.done_exams);
                    pending_exams.text(result.pending_exams);
                    all_exams_sessions.text(result.all_exams_sessions);
                }
            });

            self._rpc({
                'route': '/get_exam_chart_details',
                'params': {}
            }).done(function(result) {
                self.render_line_chart(result);
                self.render_pie_chart(result);
            });
        }
    });
    core.action_registry.add('exam_main_dashboard', ExamDashboard);

    return ExamDashboard;

});
