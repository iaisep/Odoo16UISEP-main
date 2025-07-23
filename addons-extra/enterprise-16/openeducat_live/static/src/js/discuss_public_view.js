/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import { clear } from '@mail/model/model_field_command';
import  '@mail/models/discuss_public_view';

registerPatch({
    name: 'DiscussPublicView',
    recordMethods: {
        async switchToThreadView() {
            this.update({
                threadViewer: {
                    extraClass: 'flex-grow-1',
                    hasMemberList: true,
                    hasThreadView: true,
                    hasTopbar: true,
                    thread: this.channel,
                },
                welcomeView: clear(),
            });
            if (this.isChannelTokenSecret) {
                // Change the URL to avoid leaking the invitation link.
                window.history.replaceState(window.history.state, null, `/discuss/channel/${this.channel.id}${window.location.search}`);
            }
            if (this.channel.defaultDisplayMode === 'video_full_screen') {
                await this.channel.toggleCall({ startWithVideo: true });
                setTimeout(() => {
                    if (this.threadView) {
                        if (this.threadView.rtcCallViewer) {
                            this.threadView.rtcCallViewer.activateFullScreen();
                        }
                    }
                }, 100);
            }
        }
    },
    fields: {

    },
});
