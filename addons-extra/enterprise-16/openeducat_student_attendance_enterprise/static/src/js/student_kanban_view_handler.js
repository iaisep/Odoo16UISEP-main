/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { patch } from 'web.utils';

patch(KanbanRecord.prototype, 'openeducat_student_attendance_enterprise.kanban_record', {
    onGlobalClick(ev) {
        if(this.props.record.resModel == 'op.student' && $(ev.target).parents('.o_op_student_attendance_kanban').length){
            var action = {
                type: 'ir.actions.client',
                name: 'Confirm',
                tag: 'student_attendance_kiosk_confirm',
                student_id: this.props.record.data.id,
                student_name: this.props.record.data.name,
            };
            this.action.doAction(action);
        } else {
            this._super(...arguments);
        }
    }
});
