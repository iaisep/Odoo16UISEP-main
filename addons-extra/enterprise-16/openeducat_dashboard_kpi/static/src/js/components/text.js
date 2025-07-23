/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { Component, onWillUpdateProps, useState} = owl;
import GlobalFunction from 'openeducat_dashboard_kpi.FormattingFunction';

export class Text extends CharField {
    setup() {
        super.setup();
        this.state= useState(this.getTextValues(this.props));

        onWillUpdateProps((nextProps) => {
            Object.assign(this.state, this.getTextValues(this.props));
        });
    }

    getTextValues(props) {
        var add_text_info;
        var field = props.record.data;
        var rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color)
        var font_style_selection = field.add_text_font_style;
        var font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color)
        var add_text_align_field = field.add_text_align;
        var default_icon_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.default_icon_color);
        if(field.add_text_font_style == 'custom'){
            var add_text_bold = (field.add_text_custom_bold == true) ? 'bold' : 'normal';
            var add_text_italic = (field.add_text_custom_italic == true) ? 'italic' : 'normal';
            var add_text_font_size = field.add_text_custom_font_size;
            add_text_info = {
                name: field.name,
                default_icon: field.default_icon,
                main_content : field.add_text_main_content,
                background_color : rgba_background_color,
                default_icon_color_rgba_format: default_icon_color_rgba_format,
                font_color : font_color_rgba_format,
                font_style_selection : font_style_selection,
                add_text_bold : add_text_bold,
                add_text_italic : add_text_italic,
                add_text_font_size : add_text_font_size,
                add_text_align_field : add_text_align_field
            }
        }else{
            add_text_info = {
                name: field.name,
                default_icon: field.default_icon,
                default_icon_color_rgba_format: default_icon_color_rgba_format,
                main_content : field.add_text_main_content,
                background_color : rgba_background_color,
                font_color : font_color_rgba_format,
                font_style_selection : font_style_selection,
                add_text_align_field : add_text_align_field
            }
        }

        return add_text_info
    }
};

Text.template = 'add_text_element_preview';
registry.category("fields").add("dashboard_add_text_widget", Text);
