odoo.define('openeducat_web.portal_view', function (require) {
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

var PortalViewWidget = publicWidget.Widget.extend({
        selector: '.student_portal_view',
        init: function(){
            $('.list-group-item').addClass('dashboard_element_main_body');
            var $portalList = $('.o_portal_docs .list-group-item');
            for(var tile = 0; tile < $portalList.length; tile++){
                $($portalList[tile]).wrap("<div class='col-12 col-sm-12 col-md-6 col-lg-4 p-2' ></div>");
            }
            this._super.apply(this,arguments);
        },
        start: function () {
            return this._super();
        },
    });

    return PortalViewWidget;
    //websiteRootData.websiteRootRegistry.add(PortalViewWidget, '.student_portal_view');
});
