/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { onWillStart, useRef, useState, useEffect, onWillUpdateProps } = owl;
import { loadCSS, loadJS } from "@web/core/assets";
import GlobalFunction from 'openeducat_dashboard_kpi.FormattingFunction';
import { format } from 'web.field_utils';

export class Graph extends CharField {

    setup() {
        super.setup();
        this.chartRef = useRef('chartRef');
        this.MyChart = null;
        this.state = useState({
            message: this.getMessage(this.props)
        });

        onWillStart(async () => {
            await loadJS("/openeducat_dashboard_kpi/static/lib/js/Chart.bundle.min.js");
            await loadJS("/openeducat_dashboard_kpi/static/lib/js/chartjs-plugin-datalabels.js");
            await loadCSS("/openeducat_dashboard_kpi/static/lib/css/Chart.min.css");
        });

        onWillUpdateProps((nextProps) => {
            Object.assign(this.state, {
                message: this.getMessage(nextProps),
            });
        });

        useEffect(() => {
            if(!this.state.message) {
                this.prepareChart();
            } else {
                if(this.MyChart){
                    this.MyChart.destroy();
                }
            }
        });
    }

    prepareChart() {
        var field = this.props.record.data;
        var chart_name;
        if (field.name) chart_name = field.name;
        else if (field.model_name) chart_name = field.model_id.data.display_name;
        else chart_name = "Name";

        this.chart_type = this.props.record.data.type_of_element.split('_')[0];
        this.chart_data = JSON.parse(this.props.record.data.chart_data);

        switch (this.chart_type) {
            case "pie":
            case "doughnut":
            case "polarArea":
                this.chart_family = "circle";
                break;
            case "bar":
            case "horizontalBar":
            case "line":
            case "area":
                this.chart_family = "square"
                break;
            default:
                this.chart_family = "none";
                break;
        }

        //if (this.chart_family === "circle") {
        //    if (this.chart_data && this.chart_data['labels'].length > 30) {
        //        this.$el.find(".card-body").empty().append($("<div style='font-size:20px;'>Too many records for selected Chart Type. Consider using <strong>Domain</strong> to filter records or <strong>Record Limit</strong> to limit the no of records under <strong>30.</strong>"));
        //        return;
        //    }
        //}
        this.renderChart();
    }

    renderChart() {
        var self = this;
        if (this.props.record.data.chart_data_calculation_field_2.count && this.props.record.data.type_of_element === 'bar_chart') {
            var self = this;
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
                            var selection = self.chart_data.selection;
                            if (selection === 'monetary') {
                                var currency_id = self.chart_data.currency;
                                var data = GlobalFunction.number_shorthand_function(value, 1);
                                data = GlobalFunction.currency_monetary_function(data, currency_id);
                                return data;
                            } else if (selection === 'custom') {
                                var field = self.chart_data.field;
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
        chart_plugin.push(ChartDataLabels);
        this.MyChart = new Chart(this.chartRef.el, {
            type: this.chart_type === "area" ? "line" : this.chart_type,
            plugins: chart_plugin,
            data: {
                labels: this.chart_data['labels'],
                datasets: this.chart_data.datasets,
            },
            options: {
                maintainAspectRatio: false,
                animation: {
                    easing: 'easeInQuad',
                },

                layout: {
                    padding: {
                        bottom: 0,
                    }
                },
                scales: scales,
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
        if (this.chart_data && this.chart_data["datasets"].length > 0) {
            this.ChartColors(this.props.record.data.chart_theme_selection, this.MyChart, this.chart_type, this.chart_family, this.props.record.data.show_data_value);
        }
    }

    ChartColors(palette, MyChart, ChartType, ChartFamily, show_data_value) {
        var self = this;
        var currentPalette = "cool";
        if (!palette) palette = currentPalette;
        currentPalette = palette;

        /*Gradients
          The keys are percentage and the values are the color in a rgba format.
          You can have as many "color stops" (%) as you like.
          0% and 100% is not optional.*/
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
                var datasets = MyChart.config.data.datasets[0];
                var setsCount = datasets.data.length;
                break;
            case "bar":
            case "horizontalBar":
            case "line":
                var datasets = MyChart.config.data.datasets;
                var setsCount = datasets.length;
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
                options.legend.position = 'top';
                options.layout.padding.top = 10;
                options.layout.padding.bottom = 20;
            } else {
                options.legend.position = 'bottom';
            }

            options = this.HideFunction(options, this.props.record.data, ChartFamily, chartType);

            options.plugins.datalabels.align = 'center';
            options.plugins.datalabels.anchor = 'end';
            options.plugins.datalabels.borderColor = 'white';
            options.plugins.datalabels.borderRadius = 25;
            options.plugins.datalabels.borderWidth = 2;
            options.plugins.datalabels.clamp = true;
            options.plugins.datalabels.clip = false;

            options.tooltips.callbacks = {
                title: function(tooltipItem, data) {
                    var new_self = self;
                    var k_amount = data.datasets[tooltipItem[0].datasetIndex]['data'][tooltipItem[0].index];
                    var selection = new_self.chart_data.selection;
                    if (selection === 'monetary') {
                        var currency_id = new_self.chart_data.currency;
                        k_amount = GlobalFunction.currency_monetary_function(k_amount, currency_id);
                        return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount
                    } else if (selection === 'custom') {
                        var field = new_self.chart_data.field;
                        k_amount = format.float(k_amount, Float64Array);
                        return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount + " " + field;
                    } else {
                        k_amount = format.float(k_amount, Float64Array);
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
            if (this.props.record.data.semi_circle_chart && (chartType === "pie" || chartType === "doughnut")) {
                options.rotation = 1 * Math.PI;
                options.circumference = 1 * Math.PI;
            }
        } else if (ChartFamily == "square") {
            options = this.HideFunction(options, this.props.record.data, ChartFamily, chartType);

            options.scales.xAxes[0].gridLines.display = false;
            options.scales.yAxes[0].ticks.beginAtZero = true;
            options.plugins.datalabels.align = 'end';

            options.plugins.datalabels.formatter = function(value, ctx) {
                var new_self = self;
                var selection = new_self.chart_data.selection;
                if (selection === 'monetary') {
                    var currency_id = new_self.chart_data.currency;
                    var data = GlobalFunction.number_shorthand_function(value, 1);
                    data = GlobalFunction.currency_monetary_function(data, currency_id);
                    return data;
                } else if (selection === 'custom') {
                    var field = new_self.chart_data.field;
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
                    var new_self = self;
                    var selection = new_self.chart_data.selection;
                    if (selection === 'monetary') {
                        var currency_id = new_self.chart_data.currency;
                        var data = GlobalFunction.number_shorthand_function(value, 1);
                        data = GlobalFunction.currency_monetary_function(data, currency_id);
                        return data;
                    } else if (selection === 'custom') {
                        var field = new_self.chart_data.field;
                        return GlobalFunction.number_shorthand_function(value, 1) + ' ' + field;
                    } else {
                        return GlobalFunction.number_shorthand_function(value, 1);
                    }
                }
                options.scales.xAxes[0].ticks.beginAtZero = true;
            } else {
                options.scales.yAxes[0].ticks.callback = function(value, index, values) {
                    var new_self = self;
                    var selection = new_self.chart_data.selection;
                    if (selection === 'monetary') {
                        var currency_id = new_self.chart_data.currency;
                        var data = GlobalFunction.number_shorthand_function(value, 1);
                        data = GlobalFunction.currency_monetary_function(data, currency_id);
                        return data;
                    } else if (selection === 'custom') {
                        var field = new_self.chart_data.field;
                        return GlobalFunction.number_shorthand_function(value, 1) + ' ' + field;
                    } else {
                        return GlobalFunction.number_shorthand_function(value, 1);
                    }
                }
            }
            options.tooltips.callbacks = {
                label: function(tooltipItem, data) {
                    var new_self = self;
                    var k_amount = data.datasets[tooltipItem.datasetIndex]['data'][tooltipItem.index];
                    var selection = new_self.chart_data.selection;
                    if (selection === 'monetary') {
                        var currency_id = new_self.chart_data.currency;
                        k_amount = GlobalFunction.currency_monetary_function(k_amount, currency_id);
                        return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount
                    } else if (selection === 'custom') {
                        var field = new_self.chart_data.field;
                        k_amount = format.float(k_amount, Float64Array);
                        return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount + " " + field;
                    } else {
                        k_amount = format.float(k_amount, Float64Array);
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
                            options.scales.xAxes[0].stacked = this.props.record.data.bar_chart_stacked;
                            options.scales.yAxes[0].stacked = this.props.record.data.bar_chart_stacked;
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
        if ($(this.chartRef.el).height() < 250) {
            $(this.chartRef.el).height(250);
        }
    }

    HideFunction(options, recordData, ChartFamily, chartType) {
        return options;
    }

    getMessage(props) {
        var message = false;
        if (props.record.data.type_of_element !== 'tile' && props.record.data.type_of_element !== 'kpi' && props.record.data.type_of_element !== 'list_view') {
            if (props.record.data.model_id) {
                if (props.record.data.group_chart_field == 'date_type' && !props.record.data.chart_group_field) {
                    message = "Select Group by date to create chart based on date groupby";
                } else if (props.record.data.data_calculation_type_chart === "count" && !props.record.data.group_chart_relation) {
                    message = "Select Group By to create chart view";
                } else if (props.record.data.data_calculation_type_chart !== "count" && (props.record.data.chart_data_calculation_field.count === 0 || !props.record.data.group_chart_relation)) {
                    message = "Select Measure and Group By to create chart view";
                } else if (!props.record.data.data_calculation_type_chart) {
                    message = "Select Chart Data Count Type";
                }
            } else {
                message =  "Select a Model first.";
            }
        }

        return message;
    }

}

Graph.template = 'chart_form_view_container';

registry.category("fields").add("dashboard_pro_graph_preview", Graph);
