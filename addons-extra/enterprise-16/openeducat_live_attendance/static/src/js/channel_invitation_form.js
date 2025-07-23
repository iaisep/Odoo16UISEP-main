
/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import  '@mail/models/channel_invitation_form';

registerPatch({
    name: 'ChannelInvitationForm',
    recordMethods: {
        _attendance(e) {
            console.log(this);
            console.log(this.messaging.rtc.currentRtcSession);
            this.messaging.rtc.currentRtcSession.toggleAttendance()
            console.log(this.messaging.rtc.currentRtcSession.isregister,"aaa1111")
            setTimeout(() => {
                var regitervalue = document.getElementById("Registermember").value
                if (regitervalue) {
                    this.updateshhetdata(regitervalue)
                }
            }, 100);
        },
        onclickregister() {
            var self = this
            console.log(this.messaging.rtc.currentRtcSession.isregister,"aaa")
            var regitervalue = document.getElementById("Registermember").value
            this.updateshhetdata(regitervalue)
        },
        updateshhetdata(regitervalue) {
            var self = this
            this.messaging.rpc(
                {
                    route: '/mail/rtc/session/get-sheetdata',
                    params: {
                        values: {
                            "registerid": regitervalue
                        },
                    },
                },
                { shadow: true }
            ).then(function (res) {
                self.messaging.rtc.currentRtcSession.update({ issheetdata: res })
            })
        },
        onclickSave(e) {
            var self = this
            var regitervalue = document.getElementById("Registermember").value
            if (document.getElementById("sheetdata").value) {
                var sheetvalue = document.getElementById("sheetdata").value
                self.messaging.rtc.currentRtcSession.update({ issheetid: parseInt(sheetvalue) })
                this.messaging.rpc(
                    {
                        route: '/mail/rtc/session/add-sheetid',
                        params: {
                            channel_id: this.thread.id,
                            values: {
                                "sheetid": parseInt(sheetvalue)
                            },
                        },
                    },
                    { shadow: true }
                );
            }
            this.messaging.rtc.currentRtcSession.update({ isAttendance: false, isonclickradio: false })
            this.delete();
        }
    },
    fields: {

    },
});
