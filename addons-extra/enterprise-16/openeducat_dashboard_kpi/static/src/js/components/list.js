/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { Component, onWillUpdateProps, useState } = owl;
import { format } from 'web.field_utils';

export class List extends Component {
    setup() {
        super.setup();
        var message = this.getMessage(this.props);
        var data = {
            message: message
        }
        if(!message){
            Object.assign(data, this.getListValues(this.props))
        }
        this.state = useState(data);

        onWillUpdateProps((nextProps) => {
            var message = this.getMessage(nextProps);
            var data = {
                message: message
            }
            if(!message){
                Object.assign(data, this.getListValues(nextProps))
            }
            Object.assign(this.state, data);
        });
    }

    getMessage(props) {
        var message = false;
        var rec = props.record.data;
        if (rec.type_of_element === 'list_view') {
            if (rec.list_view_type == "ungrouped") {
                if (rec.list_fields_data.count !== 0) {

                } else {
                    message = "Select Fields to show in list view.";
                }
            } else if (rec.list_view_type == "grouped") {
                if (rec.list_data_grouping.count !== 0 && rec.group_chart_relation) {
                    if (rec.group_chart_field === 'relational_type' || rec.group_chart_field === 'selection' || rec.group_chart_field === 'other' || rec.group_chart_field === 'date_type' && rec.chart_group_field) {
                    } else {
                        message =  "Select Group by Date to show list data.";
                    }
                } else {
                    message =  "Select Fields and Group By to show in list view.";
                }
            }
        }
        return message;
    }

    getListValues(props) {
        var field = props.record.data;
        var list_view_name;
        var json_list_data = JSON.parse(field.json_list_data);
        var count = field.data_calculation_value;
        if (field.name) list_view_name = field.name;
        else if (field.model_name) list_view_name = field.model_id.data.display_name;
        else list_view_name = "Name";
        if (field.list_view_type === "ungrouped" && json_list_data) {
            var index_data = json_list_data.date_index;
            for (var i = 0; i < index_data.length; i++) {
                for (var j = 0; j < json_list_data.data_rows.length; j++) {
                    var index = index_data[i]
                    var date = json_list_data.data_rows[j]["data"][index]
                    if (date) json_list_data.data_rows[j]["data"][index] = format.datetime(moment(moment(date).utc(true)._d), {}, {
                        timezone: false
                    });
                    else json_list_data.data_rows[j]["data"][index] = "";
                }
            }
        }

        if (field.json_list_data) {
            var data_rows = json_list_data.data_rows;
            for (var i = 0; i < json_list_data.data_rows.length; i++) {
                for (var j = 0; j < json_list_data.data_rows[0]["data"].length; j++) {
                    if (typeof(json_list_data.data_rows[i].data[j]) === "number" || json_list_data.data_rows[i].data[j]) {
                        if (typeof(json_list_data.data_rows[i].data[j]) === "number") {
                            json_list_data.data_rows[i].data[j] = format.float(json_list_data.data_rows[i].data[j], Float64Array)
                        }
                    } else {
                        json_list_data.data_rows[i].data[j] = "";
                    }
                }
            }
        } else json_list_data = false;
        count = json_list_data && field.list_view_type === "ungrouped" ? count - json_list_data.data_rows.length : false;
        count = count ? count <=0 ? false : count : false;

        return {
            list_view_name: list_view_name,
            json_list_data: json_list_data,
            data_rows: json_list_data['data_rows'],
            count: count,
            layout: props.record.data.list_view_layout,
        }
    }

}

List.template = 'list_view_container';
registry.category("fields").add("dashboard_pro_list_view_preview", List);
