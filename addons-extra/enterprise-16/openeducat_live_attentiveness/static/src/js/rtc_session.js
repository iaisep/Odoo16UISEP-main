/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';
import '@mail/models/rtc_session';

registerPatch({
    name: 'RtcSession',
    lifecycleHooks: {
        _created() {
            window.addEventListener('blur', this.toggleTabBlur, true);
            window.addEventListener('focus', this.toggleTabFocus, true);
            document.addEventListener('visibilitychange', this.toggleChangeTab, true);
        },
        _willDelete() {
            window.removeEventListener('blur', this.toggleTabBlur, true);
            window.removeEventListener('focus', this.toggleTabFocus, true);
            document.removeEventListener('visibilitychange', this.toggleChangeTab, true);
        }
    },

    recordMethods: {
        toggleChangeTab() {
            if (document.hidden) {
                this.toggleTab(true);

            } else {
                this.toggleTab(false);

            }
        },
        toggleTabFocus() {
            this.toggleTab(false)
        },
        toggleTabBlur() {

            this.toggleTab(true)
        },
        toggleTab(e) {
            var self = this
            this.update({ isAttentiveness: e });
            this.updateAndBroadcast({
                isAttentiveness: this.isAttentiveness,
            });
            if (e == true) {
                if (self.channel.channel.correspondent) {
                    this.messaging.rpc(
                        {
                            route: '/mail/rtc/session/is-start-time',
                            params: {
                                channel_id: self.channel.id,
                                partner_id: self.channel.channel.correspondent.id,
                                calendar_id: self.iscalendarid,
                            },
                        },
                        { shadow: true }
                    ).then(function (res) {
                        self.update({ islogid: res })
                    });
                }
            }
            if (e == false) {
                if (self.channel.channel.correspondent) {
                    this.messaging.rpc(
                        {
                            route: '/mail/rtc/session/is-end-time',
                            params: {
                                log_id: self.islogid,
                                channel_id: self.channel.id,
                            },
                        },
                        { shadow: true }
                    );
                }
            }
        },
        async toggleHandraised() {
            var self = this
            console.log("aaaaaaaaaave");
            await self.updateAndBroadcast({
                isHandRaised: !self.isHandRaised,
            })
            console.log(self.channel.channel.correspondent.id,"aaaaaaaaaaaa");
            if (self.isHandRaised) {
                console.log('111');
                if (self.channel.channel.correspondent) {
                    console.log('222');
                    this.messaging.rpc(
                        {
                            route: '/mail/rtc/session/raisedhand',
                            params: {
                                channel_id: self.channel.id,
                                partner_id: self.channel.channel.correspondent.id,
                                calendar_id: self.iscalendarid,
                                session_id: self.id,
                            },
                        },
                    )
                }
            }
        },
    },
    fields: {
        islogid: attr({ default: "" }),
        isCallEnd: attr({ default: false }),
    },
});
