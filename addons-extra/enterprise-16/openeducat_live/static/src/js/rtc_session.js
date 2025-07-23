/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';
import '@mail/models/rtc_session';

registerPatch({
    name: 'RtcSession',
    recordMethods: {
        onBroadcastTimeout() {
            if (this.emojisPopoverView && this.emojisPopoverView.contains(element)) {
                return true;
            }
            this.update({ broadcastTimer: clear() });
            this.messaging.rpc(
                {
                    route: '/mail/rtc/session/update_and_broadcast',
                    params: {
                        session_id: this.id,
                        values: {
                            is_camera_on: this.isCameraOn,
                            is_deaf: this.isDeaf,
                            is_muted: this.isSelfMuted,
                            is_screen_sharing_on: this.isScreenSharingOn,
                            is_screen_show: this.isScreenShow,
                            is_hand_raised: this.isHandRaised,
                            is_host: this.isHost,
                            is_Emoji: this.isEmoji,
                            is_Attentiveness: this.isAttentiveness ? this.isAttentiveness : false,
                        },
                    },
                },
                { shadow: true },
            );
        },
        async togglescreen(e) {
            this.updateAndBroadcast({
                isScreenShow: !this.isScreenShow,
            });
            for (const session of this.messaging.models['RtcSession'].all()) {
                if (!session.audioElement) {
                    continue;
                }
                session.audioElement.isScreenShow = this.isScreenShow;
            }
            if (this.channel.rtc) {
                await this.channel.rtc.toggleScreenDiseble()
            }
        },
        async toggleHandraised(e) {
            this.updateAndBroadcast({
                isHandRaised: !this.isHandRaised,
            });
        },

        async togglepassword(e) {
            this.updateAndBroadcast({
                isPassword: !this.isPassword,
                is_lockpassword: !this.is_lockpassword,
            });
            this.messaging.rpc(
                {
                    route: '/mail/rtc/session/lock-password',
                    params: {
                        channel_id: this.channel.id,
                        values: {
                            is_lockpassword: this.isPassword,
                        },
                    },
                },
                { shadow: true }
            )
        },
        async toggleEmoji(e) {
            this.update({ isEmoji: e })
            this.updateAndBroadcast({
                isEmoji: e,
                isFeedbackEmoji: e,
            });
            if (this.channelMember) {
                this.channelMember.update({ tempisEmoji: this.isEmoji })
            }
        },
        async toggleMeeting(e) {
            this.update({
                isMeetingLock: !this.isMeetingLock,

            });
            this.messaging.rpc(
                {
                    route: '/mail/rtc/session/lock-meeting',
                    params: {
                        channel_id: this.channel.id,
                        values: {
                            is_lockmeet: this.isMeetingLock,
                        },
                    },
                },
                { shadow: true }
            )
        },
        async selectemoji(member, as) {
            this.messaging.rpc(
                {
                    route: '/mail/rtc/session/update-and-emoji',
                    params: {
                        session_id: member.rtcSession.id,
                        values: {
                            is_badgeemoji: as.detail.unicode,
                        },
                    },
                },
                { shadow: true }
            );
        },
    },
    fields: {
        isScreenShow: attr({ default: true }),
        isMeetingLock: attr({ default: false }),
        isHandRaised: attr({ default: false }),
        isMuted: attr({ default: false }),
        isPassword: attr({ default: true }),
        isbadgeemoji: attr(),
        iscreatedpassword: attr(),
        isEmoji: attr(),
        isFeedbackEmoji: attr(),
        isHost: attr({ default: false }),
        is_lockpassword: attr({ default: true }),
        iscalendarid: attr({ default: "" }),
        isAttentiveness: attr({ default: false }),
    },
});
