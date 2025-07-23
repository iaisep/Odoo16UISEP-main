odoo.define("openeducat_web.one_signal", function(require) {
    "use strict";
    var utils = require('web.utils');
    var session = require('web.session');
    const {setCookie} = require('web.utils.cookies');

    $(document).ready(function (require) {
        //Setting User ID In cookie For One Signal
        setCookie('user_id', session.user_id ? session.user_id : session.uid);
    });
});
