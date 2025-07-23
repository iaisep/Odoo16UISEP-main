/** @odoo-module **/
import ControlPanel from 'web.ControlPanel';
import { patch } from 'web.utils';
const config = require('web.config');

// const { useState } = owl.hooks;
const { useState } = owl;
// import {useState} from "@web/core/utils/hooks";
patch(ControlPanel.prototype, "openeducat_backend_theme/static/src/js/edu/control_legacy_panel.js", {
    setup() {
        this._super(...arguments);
        this.state = useState({
            showViewSwitcherButtons: false,
            mobileSearchMode: "",
        });
        this.isMobile = config.device.isMobile;
        if (config.device.isMobile) {
            setTimeout(() => {

                $('.o_mobile_menu_NavBar').find('.o-dropdown').on('click', function(){
                    setTimeout(() => {
                        $(this).find('a').on('click', function(){
                    $('.o_mobile_menu_NavBar').removeClass('show');
                        })
                },100);
                })
                $('.o_mobile_menu_NavBar').find('.dropdown-item').on('click', function(){
                    $('.o_mobile_menu_NavBar').removeClass('show');
                })

                if($('.o_field_image').length > 0) {
                    $('.o_field_image').parent().find('.oe_title').removeClass('w-auto')
                    $('.o_field_image').parent().find('.oe_title').addClass('w-50')
                }else{
                }
                $('.o_cp_bottom_right').find('.o_dropdown_title').remove();
                $('.o_cp_bottom_right').find('.o_dropdown_chevron').remove();
                $('.o-kanban-button-new').html('<i class="fa fa-plus" title="Create"></i>');
                $('.o_list_button_add').html('<i class="fa fa-plus" title="Create"></i>');
            }, 300)
        }

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
