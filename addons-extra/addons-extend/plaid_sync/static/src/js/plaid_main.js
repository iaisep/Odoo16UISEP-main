odoo.define('plaid_sync.plaid_config_widget', function(require) {
"use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    const { loadJS } = require('@web/core/assets');
    var AbstractAction = require('web.AbstractAction');

    var PlaidAccountConfigurationWidget = AbstractAction.extend({
        on_attach_callback: function () {
            if (this.exit === true) {
                this.do_action({type: 'ir.actions.act_window_close'});
            }
        },

        init: function(parent, context) {
            var self = this;
            this._super(parent, context);
            this.rec_id = context.context.rec_id;
            this.plaid_client = context.context.plaid_client;
            this.plaid_secret = context.context.plaid_secret;
            this.environment = context.context.environment;
            this.token_key = false;
            this.loaded = new Promise(function (resolve) {
                self._loadedResolver = resolve;
            });
        },

        make_token: function(){
            var self = this;
            return this._rpc({
                    model: 'online.sync.plaid',
                    method: 'create_credentials',
                    args: [self.plaid_client,self.plaid_secret]
                }).then(function(result){
                     var link_token = JSON.parse(result)
                     self.token_key=link_token.key;
                });
        },

        willStart: function () {
            var self=this;
            var token = self.make_token();
//            $.when(token, $.getScript("http://cdn.plaid.com/link/v2/stable/link-initialize.js").fail(function(jqxhr, settings, exception) {
//                debugger;
//                console.log(exception);
//            })
            $.when(token,loadJS('https://cdn.plaid.com/link/v2/stable/link-initialize.js')).then(function() {
                var plaid_options = {
                    env: self.environment,
                    token: self.token_key,
                    onSuccess: function(public_token, metadata) {
                        if (self.public_token === undefined) {
                            return self.linkSuccess(public_token, metadata);
                        }
                        else {
                            self.exit = true;
                            self._loadedResolver();
                            location.reload();
                        }
                    },
                    onEvent: function(eventName, metadata) {
                       console.log('event');
                       console.log(eventName, metadata);
                    },

                    onExit: function(err, metadata) {
                        if (err) {
                            console.log(err);
                            console.log(metadata);
                        }
//                        debugger;
//                        self.plaid_link.destroy();
//                        debugger;
//                        self.do_action({
//                             views: [[false, 'form']],
//                             name: 'Online Sync via Plaid',
//                             res_model: 'online.sync.plaid',
//                             type: 'ir.actions.act_window',
//                             target: 'current',
//                             res_id: self.rec_id,
//                         });
                    location.reload();
                    },
                }
                self.plaid_link = Plaid.create(plaid_options);
                self.plaid_link.open();
                });
            return this.loaded;
        },

        linkSuccess: function(public_token, metadata) {
            var self = this;
            metadata.environment = self.environment;
            this._rpc({
                     model: 'online.sync.plaid',
                     method: 'link_success',
                     args: [[self.id], self.rec_id, public_token, metadata],
                     context: self.context,
            }).then(function(result){
                location.reload();
            });
        },

        renderElement: function() {
            var self = this;
            if (this.exit === true) {
                return this._super.apply(this, arguments);
            }
        },
    });

    core.action_registry.add('plaid_online_sync_widget', PlaidAccountConfigurationWidget);
});
