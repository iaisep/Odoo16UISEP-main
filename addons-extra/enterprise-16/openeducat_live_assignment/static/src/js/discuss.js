/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'Discuss',
    recordMethods: {
        _created() {
            this._super(...arguments)
            this.openform = this.openform.bind(this);
        },
        openform() {
            var self = this
            console.log("object");
            if (this.thread) {
                this.messaging.rpc(
                    {
                        route: '/mail/rtc/session/add-assignment',
                        params: {
                            channel_id: this.thread.id,
                        },
                    },
                    { shadow: true }
                ).then((res) => {
                    var action = {
                        name: "Assignment",
                        type: 'ir.actions.act_window',
                        res_model: 'op.assignment',
                        views: [[false, 'form']],
                        target: 'new',
                        context: { 'default_course_id': res.course, 'default_batch_id': res.batch, 'default_subject_id': res.subject },
                    };
                    // self.do_action(action)
                    return this.env.services.action.doAction(action);
                })
            }
        },
    },
    fields: {

    },
});
