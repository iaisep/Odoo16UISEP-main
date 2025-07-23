odoo.define('openeducat_parent_enterprise.portal_view', function (require) {
    "use strict";
    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var session = require('web.session');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');
    var utils = require('web.utils');
    var _t = core._t;
    var qweb = core.qweb;
    var wUtils = require('website.utils');

    publicWidget.registry.PortalViewWidget = publicWidget.Widget.extend({
        selector: '.parent_tile_portal',
        init: function(){
            $('.list-group-item').addClass('parent_dashboard_element_main_body');
            this._super.apply(this,arguments);
        },
        start: function () {
            return this._super();
        },
    });

    return publicWidget.registry.PortalViewWidget
});
