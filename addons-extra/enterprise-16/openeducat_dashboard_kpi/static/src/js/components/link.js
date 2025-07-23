/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { Component, onWillUpdateProps, useState} = owl;
import GlobalFunction from 'openeducat_dashboard_kpi.FormattingFunction';

export class Link extends CharField {
    setup() {
        super.setup();
        this.state= useState(this.getLinkValues(this.props));

        onWillUpdateProps((nextProps) => {
            Object.assign(this.state, this.getLinkValues(this.props));
        });
    }

    getLinkValues(props) {
        var field = props.record.data;
        var rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color);
        var font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color);
        var add_link_title = field.add_link_title;
        var add_link_title_name = field.name;
        return {
            add_link_content : field.add_link_content,
            background_color : rgba_background_color,
            font_color : font_color_rgba_format,
            add_link_title : add_link_title,
            add_link_title_name : add_link_title_name
        }

    }
};

Link.template = 'add_link_element_preview';
registry.category("fields").add("dashboard_add_link_widget", Link);
