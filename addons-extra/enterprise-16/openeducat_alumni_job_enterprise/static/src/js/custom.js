odoo.define('openeducat_alumni_job_enterprise.states_on_country', function (require) {
    'use strict';

    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var session = require('web.session');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');
    var websiteRootData = require('website.root');
    var utils = require('web.utils');
    var _t = core._t;
    var qweb = core.qweb;

    var AlumnPost = publicWidget.Widget.extend({
    	events:{'change #country_dropdown': '_onchangedropdown'},
        xmlDependencies: ['/openeducat_alumni_job_enterprise/static/src/xml/custom.xml'],
        selector: '.student_portal_view',

        init: function(){
            this._super.apply(this,arguments);
        },
        start: function () {
            return this._super();
        },
        _onchangedropdown: function(ev){
            console.log("list item selected",$(ev.currentTarget).val());
            var country_id = $(ev.currentTarget).val();
            console.log(country_id);
            ajax.jsonRpc('/get/country_data', 'call',
                {
                'country_id': country_id,
                }).then(function (data) {

                if (data)
                {
                var state_data = qweb.render('GetCountryData',
                {
                    states: data['state_list'],
                });

                $('.states').html(state_data);
                }
                });
        }
    });
    return AlumnPost
//    websiteRootData.websiteRootRegistry.add(AlumnPost, '.js_get_data');

});
