/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";

export class KpiTarget extends CharField {

    onSelect(e) {
        this.props.update(e.target.value);
    }

}

KpiTarget.template = 'widget_toggle_kpi_target_view';
registry.category("fields").add("widget_toggle_kpi_target", KpiTarget);
