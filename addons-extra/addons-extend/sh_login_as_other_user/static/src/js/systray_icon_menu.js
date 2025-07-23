odoo.define('sh_login_as_other_user.UserLoginMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var _t = core._t;

    var UserLoginMenu = Widget.extend({
        name: 'user_login_menu',
        template: 'mail.systray.UserLoginMenu',
        events: {
            'click .userLogin': '_onLoginUserClick',
        },
        _onLoginUserClick: function (ev) {
            ev.preventDefault();
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t("Login AS"),
                views: [
                    [false, 'form']
                ],
                res_model: 'login.other.wizard',
                target: 'new',
            })
        },
        start: function () {
            var self = this;
            this._rpc({
                model: 'res.users',
                method: 'check_login_enabled',
                args: [session.uid],
            })
                .then(function (result) {
                    if (result) {
                        self.$el.removeClass('d-none');
                    } else {
                        self.$el.addClass('d-none');
                    }
                });
            return this._super();
        },
    });
    SystrayMenu.Items.push(UserLoginMenu);
    return UserLoginMenu;
});