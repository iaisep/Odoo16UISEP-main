/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import '@mail/models/call_action_list_view';

registerPatch({
    name: 'CallActionListView',
    recordMethods: {
        async onClickToggleAudioCall(ev) {
            if (this.thread.hasPendingRtcRequest) {
                return;
            }
            if (this.isCallEnd) {
                return
            }
            this.messaging.rtc.currentRtcSession.update({ isCallEnd: true })
            var self = this
            if (this.thread) {
                if (this.messaging) {
                    console.log("okay");
                    this.messaging.rpc(
                        {
                            route: '/mail/rtc/session/start-end-meeting',
                            params: {
                                channel_id: this.thread.id,
                                meeting: 'end',
                                host: this.messaging.rtc.currentRtcSession.isHost
                            },
                        },
                    ).then(function (res) {
                        self.update({ isCallEnd: res })
                        self.messaging.rtc.currentRtcSession.update({ isCallEnd: res })
                        self._super(...arguments)

                    });
                }
            }
        },
    },
    fields: {
        isCallEnd: attr({ default: false }),

    },
});
