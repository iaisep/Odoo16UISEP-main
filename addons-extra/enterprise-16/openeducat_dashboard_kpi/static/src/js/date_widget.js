odoo.define("dashboard_pro.date_widget", function(require) {
    "use strict";
    var datepicker = require("web.datepicker");

    datepicker.DateWidget.include({

        _onDateTimePickerShow: function() {
            this._super.apply(this, arguments);
            if (this.name === "dashboard") {
                window.removeEventListener('scroll', this._onScroll, true);
            }
        },
    });
    return datepicker;
});
