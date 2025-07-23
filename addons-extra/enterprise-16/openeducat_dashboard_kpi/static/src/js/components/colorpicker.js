/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { onWillStart, useRef, useState, useEffect } = owl;
import { loadCSS, loadJS } from "@web/core/assets";

export class ColorPicker extends CharField {

    setup() {
        super.setup();
        this.colorPicker = useRef('colorPicker');
        onWillStart(async () => {
            await loadJS("/openeducat_dashboard_kpi/static/lib/js/spectrum.js");
            await loadCSS("/openeducat_dashboard_kpi/static/lib/css/spectrum.css");
        });

        useEffect(() => {
            this.renderColorPicker();
        });
    }

    onChangeCapacity(e) {
        this.props.update(this.props.value.split(',')[0].concat("," + e.target.value));
    }

    onChangeColor(e, tinycolor) {
        this.props.update(tinycolor.toHexString().concat("," + this.props.value.split(',')[1]))
    }

    renderColorPicker() {
        var $colorPicker = $(this.colorPicker.el).spectrum({
            color: this.props.value.split(',')[0],
            showInput: true,
            hideAfterPaletteSelect: true,
            clickoutFiresChange: true,
            showInitial: true,
            preferredFormat: "rgb",
        });
        $colorPicker.on('change.spectrum', this.onChangeColor.bind(this))
    }

}

ColorPicker.template = 'dashboard_pro_color_picker_opacity_view';

registry.category("fields").add("dashboard_pro_color_picker", ColorPicker);
