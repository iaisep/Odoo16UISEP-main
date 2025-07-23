odoo.define('openeducat_live.createmeeting', function(require) {
    "use strict";

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');

    const { Component } = owl;

    const CreateMeeting = AbstractAction.extend({
        events:{
            'click #createMeet': '_onclick',
        },
        init: function(parent, params){
            this._super.apply(this,arguments);
            this.params = params.params;

        },
        start: function () {
            var self = this
            this._super.apply(this,arguments).then( function(){

                self._rpc({
                    model: 'calendar.event',
                    method: 'search_read',
                    kwargs: {
                        domain: [['id', '=', self.params.meeting_id]],
                        fields: ['id', 'is_start_meeting'],
                    }
                }).then((res)=>{
                    if(!res[0].is_start_meeting){
                        self._rpc({
                            model: 'calendar.event',
                            method: 'write',
                            args: [self.params.meeting_id, {
                                is_start_meeting: true
                            }]
                        }).then((res)=>{
                            location.reload();
                        });
                    } else{
                        self._rpc({
                            model: 'calendar.event',
                            method: 'action_create_meet',
                            args: [self.params.meeting_id]
                        }).then((res)=>{
                            self.data = res.context
                            window.location = res.context.url;
                            self.startMeeting();
                        })

                    }
                })
            });

        },

        startMeeting: async function(){
            const discuss = await Component.env.services;
            const modelManager = await discuss.messaging.modelManager;
            const messaging = await modelManager.models['mail.thread'];

            var currentThread = messaging.create({
                id: parseInt(this.data.channel),
                model: 'mail.channel'
            })
            if (modelManager.messaging.rtc){
                if (!modelManager.messaging.rtc.channel) {
                    currentThread.toggleCall({ startWithVideo: true });
                }
            }
            await currentThread.open();
            var changeView = setInterval(() => {
                if (!$('#messagelist').hasClass('w-100')) {
                    if ($('#messagelist').hasClass('col-md-3') && $('.o_DiscussSidebar').hasClass('d-none')) {
                        clearInterval(changeView)
                    }
                }
                $('.o_DiscussSidebar').addClass('d-none');
                $('.o_ChannelMemberList').removeClass('d-none');
                $('#messagelist').removeClass('w-100');
                $('#messagelist').addClass('col-md-3');
            }, 400)
        },
    });
    core.action_registry.add('create_meet_calendar', CreateMeeting);
    return CreateMeeting;
});
