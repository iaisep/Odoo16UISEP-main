/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import  '@mail/models/rtc';

registerPatch({
    name: 'Rtc',
    recordMethods: {
        async toggleScreenDiseble() {
            const isScreenShow = this.currentRtcSession.isScreenShow
            this.currentRtcSession.updateAndBroadcast({ isScreenShow: isScreenShow });
            await this._updateLocalAudioTrackEnabledState()
        },
        async _updateLocalAudioTrackEnabledState(){
            this._super(...arguments)
            await this.notifyPeers(this.connectedRtcSessions.map(rtcSession => rtcSession.id), {
                event: 'trackChange',
                type: 'peerToPeer',
                payload: {
                    type: 'screen',
                    state: {
                        isScreenShow: this.currentRtcSession.isScreenShow,
                    },
                },
            });
        },

        _handleTrackChange(rtcSession, { type, state }) {
            this._super(...arguments)
            const{ isScreenShow } = state;
            if (type === 'screen'){
                rtcSession.update({
                    isScreenShow: isScreenShow
                });
            }
        },
    },
    fields: {

    },
});
