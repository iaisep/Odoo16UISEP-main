/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
const { Component, onWillUpdateProps, useState } = owl;

export class ToDoList extends Component {
    setup() {
        super.setup();
        this.state = useState({
            json_todo_list_data: this.getCurrentValue(this.props),
            data_rows: this.getCurrentRows(this.props)
        });

        onWillUpdateProps((nextProps) => {
            Object.assign(this.state, {
                json_todo_list_data: this.getCurrentValue(nextProps),
                data_rows: this.getCurrentRows(nextProps)
            });
        });
    }

    getCurrentValue(props) {
        return JSON.parse(props.record.data.json_todo_list_data);
    }

    getCurrentRows(props) {
        return props.record.data.to_do_list_line.records;
    }
}

ToDoList.template = 'to_do_list_view_container';
registry.category("fields").add("dashboard_pro_to_do_list", ToDoList);
