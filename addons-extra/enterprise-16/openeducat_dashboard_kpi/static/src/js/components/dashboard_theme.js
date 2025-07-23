/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { Component, onWillStart} = owl;

export class DashboardTheme extends CharField {
    setup() {
        super.setup();
        onWillStart(() => {
            this.themes = [{
                'label': 'White',
                'name': 'White',
            },{
                'label': 'Blue',
                'name': 'blue',
            },{
                'label': 'Red',
                'name': 'red',
            },{
                'label': 'Yellow',
                'name': 'yellow',
            },{
                'label': 'Green',
                'name': 'green',
            }]
        });
    }

    onSelect(e) {
        this.props.update(e.target.value);
    }

}

DashboardTheme.template = 'dashboard_theme_view';
registry.category("fields").add("dashboard_pro_item_theme", DashboardTheme);
