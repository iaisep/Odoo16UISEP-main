/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import '@mail/models/channel_invitation_form';

registerPatch({
    name: 'ChannelInvitationForm',
    recordMethods: {
        _password(e) {
            this.messaging.rtc.currentRtcSession.togglepassword()
            this.messaging.rpc(
                {
                    route: '/mail/rtc/session/get-password',
                    params: {
                        channel_id: this.thread.id,
                    },
                },
                { shadow: true }
            ).then((res) => {
                if (this.messaging) {
                    if (this.messaging.rtc) {
                        if (this.messaging.rtc.currentRtcSession) {
                            this.messaging.rtc.currentRtcSession.update({ iscreatedpassword: res })
                        }
                    }
                }
            })
        },
    },
});
