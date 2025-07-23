/** @odoo-module **/

import SearchPanel  from "@web/legacy/js/views/search_panel";
import { patch } from 'web.utils';
const { hooks } = owl;
// const { useExternalListener, useRef, useState } = owl.hooks;
import { useExternalListener, useRef, useState } from "@web/core/utils/hooks";

import { bus } from 'web.core';
const config = require('web.config');

patch(SearchPanel.prototype, 'openeducat_backend_theme/static/src/js/edu/search_panel.js', {
    setup() {
        this._super();
        this.state.isMobile = config.device.isMobile
        setTimeout(() =>{
            $('.o_mobile_searchPanel_category').on('click', function (){
                $('.o_mobile_searchPanel_toggle').removeClass('d-none')
            })
            $('.o_mobile_searchPanel_toggle_close').on('click', function (){
                $('.o_mobile_searchPanel_toggle').addClass('d-none')
            })
            $('.o_mobile_searchPanel_toggle_show_result').on('click', function (){
                $('.o_mobile_searchPanel_toggle').addClass('d-none')
            })

        },300);
    },
});
