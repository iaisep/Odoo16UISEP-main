odoo.define('openeducat_student_attendance_enterprise.kiosk_mode', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var Session = require('web.session');

var QWeb = core.qweb;


var KioskMode = AbstractAction.extend({
    events: {
        "click .o_student_attendance_button_students": function(){ this.do_action('openeducat_student_attendance_enterprise.student_attendance_action_kanban'); },
    },

    start: function () {
        var self = this;
        core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
        self.session = Session;
        var def = this._rpc({
                model: 'res.company',
                method: 'search_read',
                args: [[['id', '=', this.session.company_id]], ['name']],
            })
            .then(function (companies){
                self.company_name = companies[0].name;
                self.company_image_url = self.session.url('/web/image', {model: 'res.company', id: self.session.company_id, field: 'logo',});
                self.$el.html(QWeb.render("StudentAttendanceKioskMode", {widget: self}));
                self.start_clock();
            });
        // Make a RPC call every day to keep the session alive
        self._interval = window.setInterval(this._callServer.bind(this), (60*60*1000*24));
        return $.when(def, this._super.apply(this, arguments));
    },

    _onBarcodeScanned: function(barcode) {
        var self = this;
        this._rpc({
                    model: 'op.student',
                    method: 'attendance_scan',
                    args: [barcode, ],
                })
                .then(function (result) {
                 var action = {
                    type: 'ir.actions.client',
                    name: 'Confirm',
                    tag: 'student_attendance_kiosk_confirm',
                    student_id: result.student_id,
                    student_name: result.student_name,
                    is_barcode : true,
                };
                  if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                    core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
                }
                self.do_action(action);
            }, function () {
                core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
            });


    },

    start_clock: function() {
        this.clock_start = setInterval(function() {this.$(".o_student_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));}, 500);
        // First clock refresh before interval to avoid delay
        this.$(".o_student_attendance_clock").show().text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));
    },

    destroy: function () {
        core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
        clearInterval(this.clock_start);
        clearInterval(this._interval);
        this._super.apply(this, arguments);
    },

    _callServer: function () {
        // Make a call to the database to avoid the auto close of the session
        return ajax.rpc("/openeducat_student_attendance_enterprise/kiosk_keepalive", {});
    },

});

core.action_registry.add('student_attendance_kiosk_mode', KioskMode);

return KioskMode;

});
