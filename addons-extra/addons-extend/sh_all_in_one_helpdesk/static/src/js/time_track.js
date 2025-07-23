/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _lt } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
const { Component, useState, onWillUpdateProps, onWillStart, onWillDestroy } = owl;
export class TaskTimeCounter extends Component {
    setup() {
        const rpc = useService("rpc");
        this.orm = useService('orm');
        this.state = useState({
            // duration is expected to be given in minutes
            duration:
                this.props.value !== undefined ? this.props.value : this.props.record.data.duration,
        });
        const userService = useService("user");
        this.actionService = useService("action");

        onWillStart(async () => {
            var self = this;
            let sh_id;
            if ($.isNumeric((this.props.record.data.id))) {
                sh_id = this.props.record.data.id
            } else if (this.props.record.resId) {
                sh_id = this.props.record.resId
            }
            const result = await this.orm.call('sh.helpdesk.ticket', 'get_duration', [sh_id]);
            this.state.duration += result;
            if (this.props.record.data.start_time) {
                this._runTimer();
            }
        });


    }
    get sh_duration() {
        if (this.state.duration) {
            return moment.utc(this.state.duration).format("HH:mm:ss")
            // formatMinutes(this.state.duration);
        }
        else {
            return 0;
        }
    }
    _runTimer() {
        this.timer = setTimeout(() => {
            if (this.props.record.data.start_time) {
                this.state.duration += 1000;
                this._runTimer();
            }
        }, 1000);
    }

}

TaskTimeCounter.template = "web.TaskTimeCounter";
TaskTimeCounter.props = {
    ...standardFieldProps,
};

TaskTimeCounter.supportedTypes = ["float"];
TaskTimeCounter.displayName = _lt("Time");
registry.category("fields").add("task_time_counter", TaskTimeCounter);
