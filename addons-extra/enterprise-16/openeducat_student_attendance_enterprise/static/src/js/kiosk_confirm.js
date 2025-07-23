odoo.define('openeducat_student_attendance_enterprise.kiosk_confirm', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var QWeb = core.qweb;


var KioskConfirm = AbstractAction.extend({
    events: {
        "click .o_student_attendance_back_button": function () { this.do_action(this.next_action, {clear_breadcrumbs: true}); },
        "click .o_student_attendance_sign_in_out_icon": _.debounce(function () {
            var self = this;
            this._rpc({
                    model: 'op.student',
                    method: 'attendance_manual',
                    args: [[this.student_id], this.next_action],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.action_manager.notifications.add(result.warning,{
                            type: 'warning',
                        });
                    }
                });
        }, 200, true),
        'click .o_student_attendance_pin_pad_button_0': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 0); },
        'click .o_student_attendance_pin_pad_button_1': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 1); },
        'click .o_student_attendance_pin_pad_button_2': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 2); },
        'click .o_student_attendance_pin_pad_button_3': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 3); },
        'click .o_student_attendance_pin_pad_button_4': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 4); },
        'click .o_student_attendance_pin_pad_button_5': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 5); },
        'click .o_student_attendance_pin_pad_button_6': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 6); },
        'click .o_student_attendance_pin_pad_button_7': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 7); },
        'click .o_student_attendance_pin_pad_button_8': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 8); },
        'click .o_student_attendance_pin_pad_button_9': function() { this.$('.o_student_attendance_PINbox').val(this.$('.o_student_attendance_PINbox').val() + 9); },
        'click .o_student_attendance_pin_pad_button_C': function() { this.$('.o_student_attendance_PINbox').val(''); },
        'click .o_student_attendance_pin_pad_button_ok': _.debounce(function() {
            var self = this;
            this.$('.o_student_attendance_pin_pad_button_ok').attr("disabled", "disabled");
            if (!this.selected_att_id){
                self.action_manager.notifications.add('Please Select the Attendance Sheet',{
                    type: 'warning',
                });
            }else{
            this._rpc({
                    model: 'op.student',
                    method: 'attendance_manual',
                    args: [[this.student_id], this.next_action, this.$('.o_student_attendance_PINbox').val(), this.selected_att_id],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.action_manager.notifications.add(result.warning,{
                            type: 'warning',
                        });
                        self.$('.o_student_attendance_PINbox').val('');
                        setTimeout( function() { self.$('.o_student_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                    }
                });
        }}, 200, true),

        'change input[type="radio"]': '_OnchangeAttendance'
    },


    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.action_manager = parent;
        this.next_action = 'openeducat_student_attendance_enterprise.student_attendance_action_kiosk_mode';
        this.student_id = action.student_id;
        this.student_name = action.student_name;
        this.is_barcode = action.is_barcode;
    },

    start: function () {
        var self = this;
        var sheet_count = 0
        this._rpc({
                    model: 'op.student',
                    method: 'get_attendance_sheets',
                    args: [this.student_id, ],
                })
                .then(function (result) {
                    for (var key in result[0]){
                        if (result[0].hasOwnProperty(key))
                        {
                            self.attendance_sheets = result[0]
                            self.max_id = result[1]['is_selected']
                            self.selected_att_id = result[1]['is_selected']
                            sheet_count++

                        }
                        else{
                            self.attendance_sheets = {}
                        }
                    }

                    if (self.is_barcode == true){
                        if (sheet_count > 1 || sheet_count == 0){
                            self.$el.html(QWeb.render("StudentAttendanceKioskBarcode", {widget: self}));
                          if (sheet_count >1){
                            setTimeout(function(){
                                self._rpc({
                                    model: 'op.student',
                                    method: 'attendance_action',
                                    args: [[self.student_id], self.next_action, self.selected_att_id],
                                })
                                .then(function(result) {
                                    if (result.action) {
                                        self.do_action(result.action);
                                    } else if (result.warning) {
                                        self.action_manager.notifications.add(result.warning,{
                                            type: 'warning',
                                        });
                                    }
                                });

                            }, 5000)};
                            }
                        else {
                            self._rpc({
                                    model: 'op.student',
                                    method: 'attendance_action',
                                    args: [[self.student_id], self.next_action, self.selected_att_id],
                                })
                                .then(function(result) {
                                    if (result.action) {
                                        self.do_action(result.action);
                                    } else if (result.warning) {
                                        setTimeout( function() { self.$('.o_student_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                                    }
                                });
                                }
                       }

                    else{
                        self.$el.html(QWeb.render("StudentAttendanceKioskConfirm", {widget: self}));
                    }
                self.start_clock();

                });
        return self._super.apply(this, arguments);
    },



    start_clock: function () {
        this.clock_start = setInterval(function() {this.$(".o_student_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));}, 500);
        // First clock refresh before interval to avoid delay
        this.$(".o_student_attendance_clock").show().text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));
    },

    destroy: function () {
        clearInterval(this.clock_start);
        this._super.apply(this, arguments);
    },

    _OnchangeAttendance: function(e){
        var value = this.$("input[type='radio']:checked"). val();
        this.selected_att_id = value;

    }
});

core.action_registry.add('student_attendance_kiosk_confirm', KioskConfirm);

return KioskConfirm;

});
