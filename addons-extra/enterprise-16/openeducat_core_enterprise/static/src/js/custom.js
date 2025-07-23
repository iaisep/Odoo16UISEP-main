odoo.define('openeducat_core_enterprise.batch_on_courses', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var session = require('web.session');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');
    var utils = require('web.utils');
    var _t = core._t;
    var qweb = core.qweb;

    var SubjectRegister = publicWidget.Widget.extend({
        selector: '.js_get_data',
        events:{'change #course_dropdown': '_onchangedropdown'},
        xmlDependencies: ['/openeducat_core_enterprise/static/src/xml/custom.xml'],

        init: function(){
            this._super.apply(this,arguments);
        },
        start: function () {
            return this._super();
        },
        _onchangedropdown: function(ev){
            var course_id = $(ev.currentTarget).val();
            ajax.jsonRpc('/get/course_data', 'call',{
                'course_id': course_id,
            }).then(function (data) {
                if (data){
                    var batch_data = qweb.render('GetBatchData',{
                        batches: data['batch_list'],
                    });
                    $('.batches').html(batch_data);

                    if(data){
                        var subject_data = qweb.render('GetSubjectData',{
                            subjects: data['subject_list']
                        });
                        $('.subjects').html(subject_data);
                    }
                }
            });
        }

    });
    publicWidget.registry.SubjectRegister = SubjectRegister;

    return SubjectRegister;
});
