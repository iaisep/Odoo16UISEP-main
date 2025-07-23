/** @odoo-module **/

import { getMessagingComponent } from "@mail/utils/messaging_component";

import AbstractAction from 'web.AbstractAction';

const { Component } = owl;
import { DiscussWidget } from '@mail/widgets/discuss/discuss';

DiscussWidget.include({

    async on_attach_callback() {
        await this._super(...arguments);

        if (this.discuss.thread) {
            if (this.discuss.thread.rtc) {
                setTimeout(() => {
                    $('.o_ChannelMemberList').removeClass('d-none');
                    $('#messagelist').removeClass('w-100');
                }, 100);
            } else {
                $('.o_ChannelMemberList').addClass('d-none');
                $('#messagelist').addClass('w-100');
            }
        }
    }

});
