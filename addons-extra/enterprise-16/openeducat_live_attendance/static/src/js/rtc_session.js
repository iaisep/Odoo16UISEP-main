
/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import '@mail/models/rtc_session';

registerPatch({
    name: 'RtcSession',
    recordMethods: {
        async toggleAttendance() {
            var self = this
            this.updateAndBroadcast({
                isAttendance: !this.isAttendance,
            });
            self.messaging.rpc(
                {
                    route: '/mail/rtc/session/get-registerdata',
                },
                { shadow: true }
            ).then(function (res) {
                console.log(res, "resssssssss");
                self.update({ isregister: res })
            })
        },
    },
    fields: {
        isAttendance: attr({ default: false }),
        isregister: attr(),
        issheetid: attr(),
        issheetdata: attr(),
        isonclickradio: attr({ default: false }),
    },
});
