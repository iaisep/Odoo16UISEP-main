/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { onWillStart, useRef, useState, useEffect, onWillUpdateProps } = owl;
import { loadCSS, loadJS } from "@web/core/assets";
import GlobalFunction from 'openeducat_dashboard_kpi.FormattingFunction';
import { format } from 'web.field_utils';

export class KPI extends CharField {
    setup() {
        super.setup();
        this.file_type_word = {
            '/': 'jpg',
            'R': 'gif',
            'i': 'png',
            'P': 'svg+xml',
        }
        var message = this.getMessage(this.props);
        this.kpiRef = useRef('kpiRef');
        var data = {
            message: message
        }
        if(!message){
            Object.assign(data, this.getKpiValues(this.props))
        }
        this.state = useState(data);

        onWillUpdateProps((nextProps) => {
            var message = this.getMessage(nextProps);
            var data = {
                message: message
            }
            if(!message){
                Object.assign(data, this.getKpiValues(nextProps))
            }
            Object.assign(this.state, data);
        });

        useEffect(() => {
            if(!this.state.message){
                this.updateCss(this.props);
            }
        });
    }

    getKpiValues(props) {
        var self = this;
        var field = props.record.data;
        console.log(field,'.FIELD')
        var kpi_data = JSON.parse(field.kpi_data);
        var count_1 = kpi_data[0].record_data;
        var count_2 = kpi_data[1] ? kpi_data[1].record_data : undefined;
        var target_1 = kpi_data[0].target;
        var valid_date_selection = ['last_day', 'this_week', 'this_month', 'this_quarter', 'this_year'];
        var target_view = field.target_view,
            pre_view = field.prev_view;
        var rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color);
        var font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color)
        if (field.is_goal_enable) {
            var diffrence = 0.0
            diffrence = count_1 - target_1
            var acheive = diffrence >= 0 ? true : false;
            diffrence = Math.abs(diffrence);
            var deviation = Math.round((diffrence / target_1) * 100)
            if (deviation !== Infinity) deviation = deviation ? format.integer(deviation) + '%' : 0 + '%';
        }
        if (field.previous_data_field && valid_date_selection.indexOf(field.date_domain_fields) >= 0) {
            var previous_period_data = kpi_data[0].previous_data_field;
            var pre_diffrence = (count_1 - previous_period_data);
            var pre_acheive = pre_diffrence > 0 ? true : false;
            pre_diffrence = Math.abs(pre_diffrence);
            var pre_deviation = previous_period_data ? format.integer(parseInt((pre_diffrence / previous_period_data) * 100)) + '%' : "100%"
        }

        var rgba_icon_color = GlobalFunction.convert_to_rgba_function(field.default_icon_color)

        var item_info = {
            count_1: GlobalFunction.number_shorthand_function(kpi_data[0]['record_data'], 1),
            count_1_tooltip: kpi_data[0]['record_data'],
            count_2: kpi_data[1] ? String(kpi_data[1]['record_data']) : false,
            name: field.name ? field.name : field.model_id[1],
            target_progress_deviation: String(Math.round((count_1 / target_1) * 100)),
            selection_icon_field: field.selection_icon_field,
            default_icon: field.default_icon,
            icon_color: rgba_icon_color,
            target_deviation: deviation,
            target_arrow: acheive ? 'up' : 'down',
            enable_goal: field.is_goal_enable,
            previous_data_field: valid_date_selection.indexOf(field.date_domain_fields) >= 0 ? field.previous_data_field : false,
            target: GlobalFunction.number_shorthand_function(target_1, 1),
            previous_period_data: previous_period_data,
            pre_deviation: pre_deviation,
            pre_arrow: pre_acheive ? 'up' : 'down',
            target_view: field.target_view,
        }

        if (item_info.target_deviation === Infinity) item_info.target_arrow = false;
        item_info.target_progress_deviation = parseInt(item_info.target_progress_deviation) ? format.integer(parseInt(item_info.target_progress_deviation)) : "0"
        if (field.icon) {
            if (!utils.is_bin_size(field.icon)) {
                item_info['img_src'] = 'data:image/' + (self.file_type_word[field.icon[0]] || 'png') + ';base64,' + field.icon;
            } else {
                item_info['img_src'] = session.url('/web/image', {
                    model: self.model,
                    id: JSON.stringify(self.res_id),
                    field: "icon",
                    unique: format.datetime(self.recordData.__last_update).replace(/[^0-9]/g, ''),
                });
            }
        }
        if (kpi_data[1]) {
            switch (field.kpi_compare_field) {
                case "None":
                    var count_tooltip = String(count_1) + "/" + String(count_2);
                    var count = String(GlobalFunction.number_shorthand_function(count_1, 1)) + "/" + String(GlobalFunction.number_shorthand_function(count_2, 1));
                    item_info['count'] = count;
                    item_info['count_tooltip'] = count_tooltip;
                    item_info['target_enable'] = false;
                    item_info['template'] = 'kpi_preview_template_2';
                    break;
                case "Sum":
                    item_info['template'] = 'kpi_preview_template_2';
                    var count = count_1 + count_2
                    item_info['count'] = GlobalFunction.number_shorthand_function(count, 1);
                    item_info['count_tooltip'] = count;
                    item_info['target_enable'] = field.is_goal_enable;
                    var color = (target_1 - count) > 0 ? "red" : "green";
                    item_info.pre_arrow = (target_1 - count) > 0 ? "down" : "up";
                    item_info['comparison'] = true;
                    item_info['color'] = color;
                    var target_deviation = (target_1 - count) > 0 ? Math.round(((target_1 - count) / target_1) * 100) : Math.round((Math.abs((target_1 - count)) / target_1) * 100);
                    if (target_deviation !== Infinity) item_info.target_deviation = format.integer(target_deviation) + "%";
                    else {
                        item_info.pre_arrow = false;
                        item_info.target_deviation = target_deviation;
                    }
                    var target_progress_deviation = target_1 == 0 ? 0 : Math.round((count / target_1) * 100);
                    item_info.target_progress_deviation = format.integer(target_progress_deviation) + "%";
                    break;
                case "Percentage":
                    item_info['template'] = 'kpi_preview_template_2';
                    var count = parseInt((count_1 / count_2) * 100);
                    if (!count) count = 0;

                    item_info['count'] = count ? format.integer(count) + "%" : "0%";
                    item_info['count_tooltip'] = count ? count + "%" : "0%";
                    item_info.target_progress_deviation = item_info['count']
                    target_1 = target_1 > 100 ? 100 : target_1;
                    item_info.target = target_1 + "%";
                    item_info.pre_arrow = (target_1 - count) > 0 ? "down" : "up";
                    var color = (target_1 - count) > 0 ? "red" : "green";
                    item_info['target_enable'] = field.is_goal_enable;
                    item_info['comparison'] = false;
                    item_info['color'] = color;
                    item_info.target_deviation = item_info.target > 100 ? 100 : item_info.target;
                    break;
                case "Ratio":
                    var gcd = self.get_gcd(Math.round(count_1), Math.round(count_2));
                    if (count_1 && count_2) {
                        item_info['count_tooltip'] = count_1 / gcd + ":" + count_2 / gcd;
                        item_info['count'] = GlobalFunction.number_shorthand_function(count_1 / gcd, 1) + ":" + GlobalFunction.number_shorthand_function(count_2 / gcd, 1);
                    } else {
                        item_info['count_tooltip'] = count_1 + ":" + count_2;
                        item_info['count'] = GlobalFunction.number_shorthand_function(count_1, 1) + ":" + GlobalFunction.number_shorthand_function(count_2, 1);
                    }
                    item_info['target_enable'] = false;
                    item_info['template'] = 'kpi_preview_template_2';
                    break;
            }
        } else {
            if (target_view === "Number" || !field.is_goal_enable) {
                item_info['template'] = 'kpi_preview_template';
            } else if (target_view === "Progress Bar" && field.is_goal_enable) {
                item_info['template'] = 'kpi_preview_template_3';
            }
        }
        return item_info
    }

    updateCss(props) {
        var self = this;
        var field = props.record.data;
        var item_info = this.getKpiValues(props);
        var target_view = field.target_view,
            pre_view = field.prev_view;
        var $kpi_preview = $(this.kpiRef.el).children();
        var kpi_data = JSON.parse(field.kpi_data);
        var count_1 = kpi_data[0].record_data;
        var count_2 = kpi_data[1] ? kpi_data[1].record_data : undefined;
        var target_1 = kpi_data[0].target;
        if (field.is_goal_enable) {
            var diffrence = 0.0
            diffrence = count_1 - target_1
            var acheive = diffrence >= 0 ? true : false;
            diffrence = Math.abs(diffrence);
            var deviation = Math.round((diffrence / target_1) * 100)
            if (deviation !== Infinity) deviation = deviation ? format.integer(deviation) + '%' : 0 + '%';
        }
        if (field.previous_data_field && valid_date_selection.indexOf(field.date_domain_fields) >= 0) {
            var previous_period_data = kpi_data[0].previous_data_field;
            var pre_diffrence = (count_1 - previous_period_data);
            var pre_acheive = pre_diffrence > 0 ? true : false;
            pre_diffrence = Math.abs(pre_diffrence);
            var pre_deviation = previous_period_data ? format.integer(parseInt((pre_diffrence / previous_period_data) * 100)) + '%' : "100%"
        }
        var rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color);
        var font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color);
        if (!kpi_data[1]) {
            if (target_view === "Progress Bar" && field.is_goal_enable) {
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
            if (field.previous_data_field && String(previous_period_data) && valid_date_selection.indexOf(field.date_domain_fields) >= 0) {
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
            if ($kpi_preview.find('.row').children().length !== 2) {
                $kpi_preview.find('.row').children().addClass('text-center');
            }
        } else {
            switch (field.kpi_compare_field) {
                case "None":
                    var count_tooltip = String(count_1) + "/" + String(count_2);
                    var count = String(GlobalFunction.number_shorthand_function(count_1, 1)) + "/" + String(GlobalFunction.number_shorthand_function(count_2, 1));
                    item_info['count'] = count;
                    item_info['count_tooltip'] = count_tooltip;
                    item_info['target_enable'] = false;
                    break;
                case "Sum":
                    $kpi_preview.find('.target_deviation').css({
                        "color": item_info['color']
                    });
                    if (props.record.data.target_view === "Progress Bar") {
                        $kpi_preview.find('#progressbar').val(item_info.target_progress_deviation)
                    }
                    break;
                case "Percentage":
                    $kpi_preview.find('.target_deviation').css({
                        "color": item_info['color']
                    });
                    if (props.record.data.target_view === "Progress Bar") {
                        $kpi_preview.find('#progressbar').val(count)
                    }
                    break;
                case "Ratio":
                    var gcd = self.get_gcd(Math.round(count_1), Math.round(count_2));
                    if (count_1 && count_2) {
                        item_info['count_tooltip'] = count_1 / gcd + ":" + count_2 / gcd;
                        item_info['count'] = GlobalFunction.number_shorthand_function(count_1 / gcd, 1) + ":" + GlobalFunction.number_shorthand_function(count_2 / gcd, 1);
                    } else {
                        item_info['count_tooltip'] = count_1 + ":" + count_2;
                        item_info['count'] = GlobalFunction.number_shorthand_function(count_1, 1) + ":" + GlobalFunction.number_shorthand_function(count_2, 1);
                    }
                    item_info['target_enable'] = false;
                    break;
            }
        }
        $kpi_preview.css({
            "background-color": rgba_background_color,
            "color": font_color_rgba_format,
        });
    }

    get_gcd(a, b) {
        return (b == 0) ? a : this.get_gcd(b, a % b);
    }

    getMessage(props) {
        var message = false;
        if (props.record.data.model_id && props.record.data.type_of_element === "kpi") {
            if (!props.record.data.ir_model_field_2) {
                if (!(props.record.data.data_calculation_type === 'count')) {
                    if (props.record.data.store_field_data) {
                    } else {
                        message = "Select a Record field ";
                    }
                }
            } else {
                if (!(props.record.data.data_calculation_type === 'count') && !(props.record.data.data_calculation_type === 'count')) {
                    if (props.record.data.store_field_data_2 && props.record.data.store_field_data) {
                    } else {
                        message = "Select a Record fields ";
                    }
                } else if (!(props.record.data.data_calculation_type === 'count') && (props.record.data.data_calculation_type === 'count')) {
                    if (props.record.data.store_field_data_2) {
                    } else {
                        message = "Select a Record field";
                    }
                } else if ((props.record.data.data_calculation_type === 'count') && !(props.record.data.data_calculation_type === 'count')) {
                    if (props.record.data.store_field_data) {
                    } else {
                        message = "Select a Record field";
                    }
                }
            }
        } else {
            message = "Select a Model first";
        }
        console.log(message,'.MESSAGE')
        return message;
    }
}

KPI.template = 'kpi_preview_wrapper_template';

registry.category("fields").add("dashboard_pro_kpi_preview", KPI);
