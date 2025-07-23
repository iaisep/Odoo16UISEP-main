/** @odoo-module **/

import { session } from "@web/session";
import { getCookie, setCookie } from 'web.utils.cookies';
const reviewPopupShow = !!getCookie(`g2_review_${session.db}`);

// Prevent Review Pop Up On Enterprise
if(!reviewPopupShow) { setCookie(`g2_review_${session.db}`, true, 365 * 24 * 60 * 60, 'required'); }

$(document).ready(function(){
    const reviewEnt = !!getCookie(`g2_review_ent_${session.db}`);

    if(!reviewEnt){
        setTimeout(() => {
            const $el = $('<div class="g2_review_bar">We value your feedback! Would you mind sharing your thoughts and experiences with OpenEduCat? <i class="fa fa-star"/><i class="fa fa-star"/><i class="fa fa-star"/><i class="fa fa-star"/><i class="fa fa-star"/>' +
                    '<a href="https://openeducat.org/g2feedback" target="_blank"> Write Review</a>' +
                    '<button class="btn"><i class="fa fa-times"/> </button>' +
                '</div>');
            $('.o_control_panel').before($el);
            $el.show('slow');
            $el.find('button, a').on('click', (e) => {
                setCookie(`g2_review_ent_${session.db}`, true, 604800, 'required');
                $el.hide('slow');
            });
        }, 1500);
    }
})
