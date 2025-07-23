odoo.define('isep_sale_subscription_custom.grid_controller', function (require) {
    "use strict";
    
    var GridController = require('web_grid.GridController');
    var core = require('web.core');
    
    var SubscriptionGridController = GridController.extend({
        events: _.extend({}, GridController.prototype.events, {
            'click .o_grid_cell': '_onOpenCell',
        }),
    
        _onOpenCell: function (ev) {
            var self = this;
            var $cell = $(ev.currentTarget);
            var cellId = $cell.data('id');
            
            if (!cellId) return;
            
            this._rpc({
                model: 'sale.subscription.schedule',
                method: 'action_open_invoices',
                args: [cellId],
            }).then(function (action) {
                if (action) {
                    self.do_action(action);
                }
            });
        }
    });
    
    core.action_registry.add('subscription_report_grid', SubscriptionGridController);
    
    return SubscriptionGridController;
    });