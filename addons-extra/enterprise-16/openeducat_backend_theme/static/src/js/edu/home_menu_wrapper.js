odoo.define('openeducat_backend_theme.HomeMenuWrapper', function(require){
    'use strict';

    var AbstractAction = require("web.AbstractAction");
    const { HomeMenu } = require('@openeducat_backend_theme/js/edu/home_menu');
    var { action_registry } = require('web.core');
    var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
    var { ComponentAdapter, ComponentWrapper, WidgetAdapterMixin } = require('web.OwlCompatibility');

    const HomeMenuWrapper = AbstractAction.extend(WidgetAdapterMixin, StandaloneFieldManagerMixin, {
        init: function(parent, options){
            this._super.apply(this, arguments);
            StandaloneFieldManagerMixin.init.call(this);
            this.options = options;
        },

        start: async function(){
            var self = this;
            await this._super(...arguments);
            return this.load_menus().then(function (menuData) {
                self.homeMenu = new ComponentWrapper(self, HomeMenu, {
                    rootMenus: self.rootMenus,
                    allMenus: self.allMenus,
                });
                self.homeMenu.mount(self.$el.find('.o_content')[0]);
            });
        },

        load_menus: function () {
            var self = this;

            return odoo.loadMenusPromise.then( function(allMenus){
                self.allMenus = allMenus;

                return self._rpc({
                    model: 'ir.ui.menu',
                    method: 'load_menus_root',
                    args: [],
                }).then( function(menus){
                    for (var i = 0; i < menus.children.length; i++) {
                        var child = menus.children[i];
                        if (child.action === false) {
                            while (child.children && child.children.length) {
                                child = child.children[0];
                                if (child.action) {
                                    menus.children[i].action = child.action;
                                    break;
                                }
                            }
                        }
                    }
                    self.rootMenus = menus;

                    return menus;
                });
            });
        },
    });

    action_registry.add('apps_menu',HomeMenuWrapper);

    return HomeMenuWrapper;
});
