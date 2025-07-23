/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";

export class WidgetToggleKPI extends CharField {

    onSelect(e) {
        this.props.update(e.target.value);
    }

}

WidgetToggleKPI.template = 'kpi_type_selection_widget';
registry.category("fields").add("kpi_type_selection_widget", WidgetToggleKPI);
