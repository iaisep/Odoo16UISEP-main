odoo.define('annoying_notification_bar.annoying_notification', function (require) {
    "use strict";

    var session = require('web.session');
    var core = require('web.core')
    var ajax = require('web.ajax');
    var QWeb = core.qweb;

    $(function () {
        ajax.jsonRpc('/web/dataset/call_kw', 'call', {
            model: 'res.config.settings',
            method: 'verify_database',
            args: [
                []
            ],
            kwargs: {},
        }).then(function (days) {
            if (days <= 15 && days >= 0) {
                var cont = QWeb.render("OpenEduCatCoreEnt.EntContent", {});
                setTimeout(function () {
                    $('.o_control_panel').before(cont);
                    $('div#annoying_custom_notifications_bar').show('slow');
                    $(QWeb.render('OpenEduCat.expiration_panel', {'diffDays': days})).appendTo('.custom_annoying_notification_content .db_expire_info');
                }, 1500);
            }
            if (days < 0) {
                var cont = QWeb.render("OpenEduCatCoreEnt.EntContent", {});
                setTimeout(function () {
                    $('.o_control_panel').before(cont);
                    $('div#annoying_custom_notifications_bar').show('slow');
                    $(QWeb.render('OpenEduCat.expiration_panel', {'diffDays': days})).appendTo('.custom_annoying_notification_content .db_expire_info');
                    $('div#block_content').show('slow');
                }, 1500);
            }
        });
    });
});
