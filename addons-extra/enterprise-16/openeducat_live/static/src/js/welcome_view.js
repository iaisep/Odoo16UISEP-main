/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import '@mail/models/welcome_view';

registerPatch({
    name: 'WelcomeView',
    recordMethods: {
        onComponentUpdate() {

            this.messaging.rpc(
                {
                    route: '/mail/rtc/session/check-lock',
                    params: {
                        channel_id: this.channel.id,
                    },
                },
                { shadow: true }
            ).then((res) => {
                setTimeout(() => {
                    if (res) {
                        $('.input_password').removeClass('d-none')
                        $('.input_password').addClass('d-show')
                    } else {
                        $('.input_password').removeClass('d-show')
                        $('.input_password').addClass('d-none')
                    }
                    $('.o_DiscussPublicView').addClass('justify-content-center')
                }, 50)
            })
        },
        onClickJoinButton(ev) {
            var self = this
            var password = document.getElementById("password").value
            var temp = '';
            var partner = '';
            if (this.messaging) {
                if (this.messaging.currentUser) {
                    if (this.messaging.currentUser.id) {
                        temp = this.messaging.currentUser.id;
                        partner = this.messaging.currentPartner.id;
                    }
                }
            }
            this.messaging.rpc(
                {
                    route: '/mail/rtc/session/welcomepage',
                    params: {
                        channel_id: this.channel.id,
                        values: {
                            "password": password,
                            "users_id": temp,
                            "partner_id": partner,
                        },
                    },
                },
                { shadow: true }
            ).then((res) => {
                if (res == true) {
                    this.joinChannel()
                    // this.joinChannel().then(() => {
                    //     var changeView = setInterval(() => {
                    //         $('.o_ThreadView_channelMemberList').removeClass('d-none');
                    //         $('#messagelist').removeClass('w-100');
                    //         $('#messagelist').addClass('col-md-3');
                    //         if (!$('#messagelist').hasClass('w-100')) {
                    //             if ($('#messagelist').hasClass('col-md-3')) {
                    //                 clearInterval(changeView)
                    //             }
                    //         }
                    //     }, 200)
                    // })
                }
                else if (res == 'incorrect-password') {
                    $('#pass').show();
                }
                else if (res == 'lock-meeting') {
                    $('#myModal').modal('show');
                }
            })
        },
        onKeydownGuestNameInput(ev) {
            if (ev.key === 'Enter') {
                this.onClickJoinButton();
            }
        }
    },
    fields: {

    },
});
