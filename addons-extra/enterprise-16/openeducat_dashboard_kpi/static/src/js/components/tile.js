/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { onWillStart, useRef, useState, useEffect, onWillUpdateProps } = owl;
import { loadCSS, loadJS } from "@web/core/assets";
import GlobalFunction from 'openeducat_dashboard_kpi.FormattingFunction';
import { format } from 'web.field_utils';

export class Tile extends CharField {
    setup() {
        super.setup();
        this.file_type_word = {
            '/': 'jpg',
            'R': 'gif',
            'i': 'png',
            'P': 'svg+xml',
        }
        this.state = useState(this.getTileValues(this.props));
        this.tileRef = useRef('tileRef');
        onWillUpdateProps((nextProps) => {
            Object.assign(this.state, this.getTileValues(this.props));
        });

        useEffect(() => {
            this.updateCss();
        });
    }

    getTileValues(props) {
        var self = this;
        var field = props.record.data;
        var $val;
        var item_info;
        var rgba_background_color, font_color_rgba_format, rgba_icon_color;
        rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color)
        font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color)
        rgba_icon_color = GlobalFunction.convert_to_rgba_function(field.default_icon_color)
        item_info = {
            name: field.name,
            count: GlobalFunction.number_shorthand_function(field.data_calculation_value, 1),
            selection_icon_field: field.selection_icon_field,
            default_icon: field.default_icon,
            icon_color: rgba_icon_color,
            count_tooltip: field.data_calculation_value,
        }
        if (field.icon) {

            if (!(/^\d+(\.\d*)? [^0-9]+$/).test(field.icon)) {
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
        if (!field.name) {
            if (field.model_name) {
                item_info['name'] = field.model_id[1];
            } else {
                item_info['name'] = "Name";
            }
        }


        switch (field.layout) {
            case 'layout1':
                item_info['template'] = 'database_list_layout1'
                break;

            case 'layout2':
                item_info['template'] = 'dashboard_list_layout2'
                break;

            case 'layout3':
                item_info['template'] = 'db_list_preview_layout3'
                break;

            case 'layout4':
                item_info['template'] = 'dashboarb_list_layout_4'
                break;

            case 'layout5':
                item_info['template'] = 'dashboard_list_layout5'
                break;

            case 'layout6':
                item_info['template'] = 'dashboard_list_preview_layout_6'
                break;

            case 'state_layout_1':
                item_info['template'] = 'state_list_preview_layout'
                break;

            case 'state_layout_2':
                item_info['template'] = 'state_list_preview_layout_1'
                break;

            default:
                item_info['template'] = 'db_list_preview'
                break;

        }
        return item_info;
    }

    updateCss() {
        var self = this;
        var $val = $(this.tileRef.el).children();
        var field = this.props.record.data;
        var rgba_background_color, font_color_rgba_format, rgba_icon_color;
        rgba_background_color = GlobalFunction.convert_to_rgba_function(field.background_color)
        font_color_rgba_format = GlobalFunction.convert_to_rgba_function(field.font_color)
        rgba_icon_color = GlobalFunction.convert_to_rgba_function(field.default_icon_color)
        switch (this.props.record.data.layout) {
            case 'layout1':
                $val.css({
                    "background-color": rgba_background_color,
                    "color": font_color_rgba_format
                });
                break;

            case 'layout2':
                var rgba_dark_background_color_l2 = GlobalFunction.convert_to_rgba_function(self.dark_color_generator(field.background_color.split(',')[0], field.background_color.split(',')[1], -10));
                $val.find('.dashboard_icon_layout_2').css({
                    "background-color": rgba_dark_background_color_l2,
                });
                $val.css({
                    "background-color": rgba_background_color,
                    "color": font_color_rgba_format
                });
                break;

            case 'layout3':
                $val.css({
                    "background-color": rgba_background_color,
                    "color": font_color_rgba_format
                });
                break;

            case 'layout4':
                $val.find('.dashboard_icon_layout_4').css({
                    "background-color": rgba_background_color,
                });
                $val.find('.dashboard_item_preview_customize').css({
                    "color": rgba_background_color,
                });
                $val.find('.dashboard_item_preview_delete').css({
                    "color": rgba_background_color,
                });
                $val.css({
                    "border-color": rgba_background_color,
                    "color": font_color_rgba_format
                });
                break;

            case 'layout5':
                $val.css({
                    "background-color": rgba_background_color,
                    "color": font_color_rgba_format
                });
                break;

            case 'layout6':
                $val.css({
                    "background-color": rgba_background_color,
                    "color": font_color_rgba_format
                });

                break;

            case 'state_layout_1':
                $val.css({
                    "background-color": rgba_background_color,
                    "color": font_color_rgba_format,
                });

                break;

            case 'state_layout_2':
                $val.find('.side_bar_div').css({
                    "background-color": rgba_background_color,
                    "color": font_color_rgba_format,
                });
                $val.find('.dashboard_element_info_layout_3').css({
                    "color":font_color_rgba_format
                })
                break;
        }
    }

    dark_color_generator(color, opacity, percent) {
        var self = this;
        var num = parseInt(color.slice(1), 16),
            amt = Math.round(2.55 * percent),
            R = (num >> 16) + amt,
            G = (num >> 8 & 0x00FF) + amt,
            B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1) + "," + opacity;
    }
}

Tile.template = 'list_preview_wrapper_template';

registry.category("fields").add("dashboard_pro_item_preview", Tile);
