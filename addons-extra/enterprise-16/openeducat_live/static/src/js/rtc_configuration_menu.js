/** @odoo-module **/
import { CallSettingsMenu } from '@mail/components/call_settings_menu/call_settings_menu';
import { patch } from 'web.utils';

patch(CallSettingsMenu.prototype, "openeducat_live/static/src/js/rtc_configuration_menu.js", {
    _hidescreenshare(e) {
        this.messaging.rtc.currentRtcSession.togglescreen(true)
    },
});
