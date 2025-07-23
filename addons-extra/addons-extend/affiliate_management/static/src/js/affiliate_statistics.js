odoo.define('affiliate_management.affiliate_statistics',function(require){
    "use strict";
    
    const core = require('web.core');
    const ajax = require('web.ajax');
    const rpc = require('web.rpc');
    const _t = core._t;
    const publicWidget = require('web.public.widget');
    
    
    publicWidget.registry.AffiliateStatistics = publicWidget.Widget.extend({
        selector: '.aff_stats',
        
        jsLibs: [
            '/web/static/lib/Chart/Chart.js',
        ],
        
        events: {
            'click #pills-weekly-tab': '_updateWeeklyGraphs',
            'click #pills-monthly-tab': '_updateMonthlyGraphs',
            
        },
        
        start: function() {
            var self = this;
            self.traffic_graph = self._renderTrafficGraph();
            self.order_graph = self._renderOrderGraph();
            self._updateWeeklyGraphs();
            return this._super.apply(this, arguments).then(function() {
            });
        },

        _renderTrafficGraph: function() {
            let traffic_canvas = $('canvas#trafficGraph')[0];
            let traffic_context = traffic_canvas.getContext('2d');
            let traffic_config = this._createGraphConfig("Pay Per Click", "PPC Reports", "#225cf0");
            return new Chart(traffic_context, traffic_config);
            
        },

        _renderOrderGraph: function() {
            let order_canvas = $('canvas#orderGraph')[0];
            let order_context = order_canvas.getContext('2d');
            let order_config = this._createGraphConfig("Pay Per Sale", "PPS Reports", "#584854");
            return new Chart(order_context, order_config);
        },

        _createGraphConfig: function(title, label, border_color) {
            return {
                type: 'line',
                responsive: true,
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        fill: false,
                        label: _t(label),
                        borderColor: border_color,
                        tension: 0.2,
                    }],
                },
    
                options: {
                    legend: {
                        display: true,
                        align: 'end',
                    },
                    filler: {
                        propagate: false,
                    },
                    title: {
                        display: true,
                        text: _t(title),
                        fontSize: 22,
                        fontStyle: "bold",
                        padding: 10,
                        fontColor: border_color,
                    },
                    plugins: {
                    },
                    scales: {
                        yAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: _t(label),
                            },
                            position: 'left',
                        }],
                        xAxes: [{
                            scaleLabel: {
                                display: true,
                            },
                            gridLines: {
                                display: false,
                            },
                        }],
                    },
                },
            };
        },

        _updateWeeklyGraphs: function() {
            var self = this;
            return rpc.query({
                model:'affiliate.visit',
                method:'get_traffic_daily_stats',
                args: [parseInt($('span#aff_website_id').text())]
            }).then(function(res){
                self.traffic_graph.data.labels = res.day_label;
                self.order_graph.data.labels = res.day_label;
                self.traffic_graph.data.datasets.forEach((dataset) => {
                    dataset.data = res.count_traffic;
                });
                self.order_graph.data.datasets.forEach((dataset) => {
                    dataset.data = res.count_order;
                });
                self.traffic_graph.options.scales.xAxes[0].scaleLabel.labelString = _t("Days");
                self.order_graph.options.scales.xAxes[0].scaleLabel.labelString = _t("Days");
                self.traffic_graph.update();
                self.order_graph.update();
                $('#pills-monthly-tab').removeClass('btn-primary');
                $('#pills-weekly-tab').addClass('btn-primary');
                return res;
            });
        },

        _updateMonthlyGraphs: function() {
            var self = this;
            return rpc.query({
                model:'affiliate.visit',
                method:'get_traffic_monthly_stats',
                args: [parseInt($('span#aff_website_id').text())]
            }).then(function(res){
                self.traffic_graph.data.labels = res.month_label;
                self.order_graph.data.labels = res.month_label;
                self.traffic_graph.data.datasets.forEach((dataset) => {
                    dataset.data = res.count_traffic;
                });
                self.order_graph.data.datasets.forEach((dataset) => {
                    dataset.data = res.count_order;
                });
                self.traffic_graph.options.scales.xAxes[0].scaleLabel.labelString = _t("Months");
                self.order_graph.options.scales.xAxes[0].scaleLabel.labelString = _t("Months");
                self.traffic_graph.update();
                self.order_graph.update();
                $('#pills-weekly-tab').removeClass('btn-primary');
                $('#pills-monthly-tab').addClass('btn-primary');
                return res;
            });
        },

    });

});
