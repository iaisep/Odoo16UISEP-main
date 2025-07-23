/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";
import { hasTouch } from "@web/core/browser/feature_detection";
const { HomeMenu } = require('@openeducat_backend_theme/js/edu/home_menu');
const { onMounted } = owl;
import { session } from "@web/session";
import SideMenu from 'openeducat_backend_theme.sidemenu';
import { bus } from 'web.core';
import { browser } from '@web/core/browser/browser';

export class WebClientTheme extends WebClient {

    setup() {
        super.setup(...arguments);
        this.rpc = useService("rpc");
        this.previous_url = false;
        const originalEvent = this.menuService.setCurrentMenu;
        this.menuService.setCurrentMenu = function(menu){
            originalEvent.apply(this, [menu]);
            bus.trigger('reset_side_menu', menu.actionID);
        }
        onMounted(() => {
            this.env.bus.on("home_menu_toggled", this, (toggle) => {
                this.toggleHomeMenu(toggle)
            });
            bus.on("home_menu_selected", this, (menu) => {
                this.homeMenuSelected(menu)
            });
            bus.on("reset_side_menu", this, (actionID) => {
                this.resetSidebarMenu(actionID);
            });
            this.resetSidebarMenu();
        });
    }

    resetSidebarMenu(actionID=false) {
        var state = $.bbq.getState(true);
        if(actionID && actionID != state.action){
            setTimeout(() => {
                this.resetSidebarMenu(actionID);
                return;
            }, 500);
            return;
        }
        var app = {
            'menuID': state.menu_id,
            'actionID': state.action
        }
        if(this.sidemenu){
            this.sidemenu.destroy();
        }
        this.sidemenu = new SideMenu(this);
        this.sidemenu.appendTo($('.oe_application_menu_placeholder'));
        this.sidemenu.reset_menu();
        this.sidemenu.set_menu(app);
        $('#menu_launcher').removeClass('d-none');
    }

    toggleHomeMenu(toggle) {
        this.previous_url = $.bbq.getState();
        bus.trigger('set_prev_url', $.bbq.getState());
        this.actionService.doAction('apps_menu', {});
    }

    async homeMenuSelected(menu) {
        await this.menuService.selectMenu(menu);
    }

    _loadDefaultApp() {
        this.actionService.doAction('apps_menu', {});
    }
}
WebClientTheme.components = { ...WebClient.components, HomeMenu };
