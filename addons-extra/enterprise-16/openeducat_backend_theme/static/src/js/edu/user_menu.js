/** @odoo-module **/

import {UserMenu}  from "@web/webclient/user_menu/user_menu";
import { patch } from 'web.utils';
const { hooks } = owl;
// const { useExternalListener, useRef, useState } = owl.hooks;
import { useExternalListener, useRef } from "@web/core/utils/hooks";
const { useState } = owl;
import { bus } from 'web.core';
const config = require('web.config');

patch(UserMenu.prototype, 'openeducat_backend_theme/static/src/js/edu/user_menu.js', {
    setup() {
        this._super();
        this.state = useState({
            isMobile: config.device.isMobile,
        });
        setTimeout(() =>{

            $('.o_mobile_user_menu_btn').on('click', function (){
                $('.o_mobile_user_menu').removeClass('d-none')
            })
            $('.o_mobile_user_menu_close').on('click', function (){
                $('.o_mobile_user_menu').addClass('d-none')
            })

        },300);
    },
});
