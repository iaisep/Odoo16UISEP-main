/** @odoo-module **/
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { patch } from 'web.utils';
const config = require('web.config');
var tour = require('web_tour.tour');

// const { useState } = owl.hooks;
const { useState } = owl;
// import {useState} from "@web/core/utils/hooks";
patch(ControlPanel.prototype, "openeducat_backend_theme/static/src/js/edu/control_panel.js", {
    setup() {
        this._super(...arguments);
        this.state = useState({
            showViewSwitcherButtons: false,
            mobileSearchMode: "",
        });
        this.isMobile = config.device.isMobile;
    },
//    get mobileConfig() {
//        return {
//            'isMobile': config.device.isMobile,
//            'viewType': this.__owl__.parent.props.viewType
//        }
//    },
    _onWindowClick(event) {
        if (this.state.showViewSwitcherButtons && !event.target.closest('.o_cp_switch_buttons')) {
            this.state.showViewSwitcherButtons = false;
        }
    },
    _getCurrentViewIcon() {
        const currentView = this.props.views.find((view) => {
            return view.type === this.env.view.type
        })
        return currentView.icon;
    }
});
patch(DropdownItem.prototype, "openeducat_backend_theme/static/src/js/edu/control_panel.js", {
    setup() {
        this._super(...arguments);
        this.state = useState({
            showViewSwitcherButtons: false,
            mobileSearchMode: "",
        });
        this.isMobile = config.device.isMobile;
    },
    get mobileConfig() {
        return {
            'isMobile': config.device.isMobile,
            'viewType': this.__owl__.parent.props.viewType
        }
    },
    _onWindowClick(event) {
        if (this.state.showViewSwitcherButtons && !event.target.closest('.o_cp_switch_buttons')) {
            this.state.showViewSwitcherButtons = false;
        }
    },
    _getCurrentViewIcon() {
        const currentView = this.props.views.find((view) => {
            return view.type === this.env.view.type
        })
        return currentView.icon;
    }
});
