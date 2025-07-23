odoo.define('openeducat_core_enterprise.terminology', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var session = require('web.session');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');
    var websiteRootData = require('website.root');
    var utils = require('web.utils');
    var _t = core._t;
    var qweb = core.qweb;
    var model = require('web.Model');

     fetch_data: function() {
            var self = this;
            return this._rpc({
                model: 'terminology.configuration',
                method: 'label_name_change',
            }).then(function(result) {
            });
        }
});
