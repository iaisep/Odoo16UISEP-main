/** @odoo-module **/
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { patch } from 'web.utils';
const config = require('web.config');
var tour = require('web_tour.tour');

const { useState } = owl;
// import {useState} from "@web/core/utils/hooks";

patch(DropdownItem.prototype, "openeducat_backend_theme/static/src/js/edu/DropdownItem.js", {
    setup() {
        this._super(...arguments);
        this.state = useState({
            showViewSwitcherButtons: false,
            mobileSearchMode: "",
        });
        this.isMobile = config.device.isMobile;
        if (config.device.isMobile) {
            $('.o_dropdown').on('click', function () {
                setTimeout(() => {
                    $('.o-dropdown--menu').addClass('o_dropdown_menu')
                    $('.o-dropdown--menu').addClass('dropdown-menu')
                    $('.o-dropdown--menu').addClass('show')
                }, 5)
            })
        }


    },
    get mobileConfig() {
        return {
            'isMobile': config.device.isMobile,
            'viewType': this.__owl__.parent.props.viewType
        }
    },
});
