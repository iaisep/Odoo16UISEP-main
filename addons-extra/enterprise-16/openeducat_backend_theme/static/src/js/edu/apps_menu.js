/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from 'web.utils';
const { hooks,useState } = owl;
import {useExternalListener, useRef} from "@web/core/utils/hooks";
// const { useExternalListener, useRef, useState } = owl.hooks;
import { bus } from 'web.core';

const config = require('web.config');

patch(NavBar.prototype, 'openeducat_backend_theme/static/src/js/edu/apps_menu.js', {
    setup() {
        this._super();
        this.state = useState({
            is_home_menu: false,
            isMobile: config.device.isMobile,
            prev_url: null,
        });
        bus.on('app_clicked', this, (res) => {
            this.onNavBarDropdownItemSelection(res.menu_id)
        });
        bus.on("home_menu_change", this, (res) => {
            this.state.is_home_menu = res;
            this.isMobile = config.device.isMobile;
        });
        bus.on("set_prev_url", this, (res) => {
            this.state.prev_url = res;
        });
    },

    async onClickMainMenu(e) {
        //await $.bbq.pushState('#home=apps', 2);
        this.env.bus.trigger('home_menu_toggled', true);
    },

    async onClickSideBarMenu(ev){
         ev.preventDefault();
         $('.o-menu-slide > i').toggleClass('fa-compress fa-expand');
         $('.f_launcher_content').toggleClass('mobile_views_menu_force');
         this.updateSidebar();
    },

    async onClickBackButton(e) {
        await $.bbq.pushState(this.state.prev_url, 2);
        this.state.is_home_menu = false;
        this.isMobile = config.device.isMobile;
    },

    updateSidebar: function () {
        var btn = $('.o-menu-slide');
        var $fLauncherContent = $('.f_launcher_content');
        if (!$fLauncherContent.length || window.matchMedia('(max-device-width: 1024px)').matches) {
            btn.hide();
            $fLauncherContent.removeClass('mobile_views_menu_force');
        } else {
            btn.show();
        }
        if ($fLauncherContent.hasClass('mobile_views_menu_force') || window.matchMedia('(max-device-width: 1024px)').matches) {
            $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').addClass('hidden');
            $fLauncherContent.addClass('mobile_views_menu');
            $('.o_action_manager').addClass('force_mobile');
        } else {
            $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').removeClass('hidden');
            $fLauncherContent.removeClass('mobile_views_menu');
            $('.o_action_manager').removeClass('force_mobile');
        }
    }

});
