/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import { attr, many, one } from '@mail/model/model_field';
import { clear, link } from '@mail/model/model_field_command';
import  '@mail/models/call_action_list_view';
// import { emojiCategoriesData, emojisData } from "@mail/models_data/emoji_data";
var core = require('web.core');
var QWeb = core.qweb;

registerPatch({
    name: 'CallActionListView',
    recordMethods: {
        async onClickRiseHand(ev) {
            await this.messaging.rtc.currentRtcSession.toggleHandraised();
            this.update({ isRaiseHandMessege: !this.isRaiseHandMessege })
        },
        async onClicklockMeeting(ev) {
            await this.messaging.rtc.currentRtcSession.toggleMeeting();

        },
        /**
         * @private
         * @param {KeyboardEvent} ev``
         */
        onKeydownButtonEmojis(ev) {
            if (ev.key === 'Escape' && this.emojisPopoverView) {
                this.update({
                    doFocus: true,
                    emojisPopoverView: clear(),
                });
                markEventHandled(ev, 'Composer.closeEmojisPopover');
            }
        },
        async onClickButtonEmojis(ev) {
            await this.messaging.emojiRegistry.loadEmojiData();
            if (!this.popoveremoji) {
            $(document).click((a) => {
                this.temp = 0
                if ($(a.target).hasClass('o_Composer_primaryToolButtons_emoji')) {
                    this.temp = 1
                } else if ($(a.target).hasClass('o_CallActionList_button_emoji')) {
                    this.temp = 1
                } else if ($(a.target).hasClass('o_CallActionList_buttonIconWrapper_emoji')) {
                    this.temp = 1
                } else if ($(a.target).hasClass('o_ActionList_button_emoji')) {
                    this.temp = 1
                }
                if (this.temp == 0) {
                    $('#smiley').popover('hide')
                    this.open = true
                }
            })
                this.open = true
                $('#smiley').popover({
                    html: true,
                    trigger: 'manual',
                    content: $(QWeb.render('Emogi_popover', { emoji: this.messaging.emojiRegistry.allEmojis })),
                });

            }
            $(document).click((a) => {

            });
            if (this.open) {
                $('#smiley').popover('show')
                this.open = false
            }
            else {
                $('#smiley').popover('hide')
                this.open = true
            }
            if (!this.popoveremoji) {
                this.popoveremoji = true
                $('.emoji_select').click((a) => {
                    a.preventDefault();
                    this.messaging.rtc.currentRtcSession.toggleEmoji(a.currentTarget.innerText);
                })
            }

        },
        async _onEmojiSelections(ev) {
            await this.messaging.rtc.currentRtcSession.toggleEmoji(ev.detail.unicode);
        },
    },
    fields: {
        isRaiseHandMessege: attr({ default: true }),
    },
});
