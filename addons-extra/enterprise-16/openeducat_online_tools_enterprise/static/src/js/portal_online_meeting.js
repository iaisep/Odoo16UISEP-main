odoo.define('openeducat_online_tools_enterprise.portal_online_meeting', function (require) {
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
    var wUtils = require('website.utils');
    var cookies = require('web.utils.cookies');

    var PortalOnlineMeetingWidget = publicWidget.Widget.extend({
        selector: '.online_meeting_schedule_portal',
        jsLibs: [
            '/openeducat_web/static/src/kendo_ui/js/jszip.min.js',
            '/openeducat_web/static/src/kendo_ui/js/kendo.all.min.js',
            '/openeducat_web/static/src/kendo_ui/js/kendo.timezones.min.js',
        ],
        cssLibs: [
            '/openeducat_web/static/src/kendo_ui/css/kendo.common.min.css',
            '/openeducat_web/static/src/kendo_ui/css/kendo.default.min.css',
            '/openeducat_web/static/src/kendo_ui/css/kendo.default.mobile.min.css',
        ],
        start: async function(){
            this._super.apply(this,arguments);
            var self = this;
            await this.setLocaleKendo();
        },
        setLocaleKendo: async function(){
            var self = this;
            var language = cookies.getCookie('frontend_lang').replace('_','-');

            var baseUrlMessages = 'https://kendo.cdn.telerik.com/2021.1.330/js/messages/kendo.messages.';
            var baseUrlCultures = 'https://kendo.cdn.telerik.com/2021.1.330/js/cultures/kendo.culture.';
            try{
                $.getScript(baseUrlMessages + language + ".min.js").then( function (script, textStatus) {
                    $.getScript(baseUrlCultures + language + ".min.js").then( function (script, textStatus) {
                        kendo.culture(language);
                        self.InitKendo();
                    }).fail(function(){
                        self.InitKendo();
                    });
                }).fail(function(){
                    $.getScript(baseUrlCultures + language + ".min.js").then( function (script, textStatus) {
                        kendo.culture(language);
                        self.InitKendo();
                    }).fail(function(){
                        self.InitKendo();
                    });
                });
            }catch(err){
                this.InitKendo();
            }
            return true;
        },
        InitKendo: async function(){
            var self = this;
            var today = new Date();
            var date = today.getFullYear()+'/'+(today.getMonth()+1)+'/'+today.getDate();
            var stud_id = $(".stud_id_online_meeting_parent").attr('id');
            var timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            ajax.jsonRpc("/get-online-meeting/data",'call',{
                stud_id:stud_id,
                current_timezone: timezone,
            }).then(function(data){

                var kendoData = new kendo.data.SchedulerDataSource({data : data});
                $('#online_meeting_portal_kendo').kendoScheduler({
                    date   : new Date(date),
                    editable: {
                        confirmation: false,
                        create: false,
                        destroy: false,
                        move: false,
                        editRecurringMode: "series",
                        resize:false,
                        template: $("#editor").html(),
                    },
                    majorTimeHeaderTemplate: kendo.template("<strong>#=kendo.toString(date, 'HH:mm')#</strong>"),
                    edit: function(e) {
                        e.container.find(".k-scheduler-update").hide();
                    },
                    views: [{ type: "day", eventTemplate: $("#event-template").html(),
                                dateHeaderTemplate: "<span class='k-link k-nav-day'>#=kendo.toString(date, 'ddd dd/M')#</span>",
                            },
                            { type: "week", eventTemplate: $("#event-template").html(),
                                dateHeaderTemplate: "<span class='k-link k-nav-day'>#=kendo.toString(date, 'ddd dd/M')#</span>",
                            },
                            { type: "month", eventTemplate: $("#event-template").html()},
                            {type: "agenda", selected: true, eventTemplate: $("#day-event-template").html()},
                    ],
                    dataSource:kendoData,
                });
            });
        },
    });
    publicWidget.registry.PortalOnlineMeetingWidget = PortalOnlineMeetingWidget;
    return PortalOnlineMeetingWidget;
});
