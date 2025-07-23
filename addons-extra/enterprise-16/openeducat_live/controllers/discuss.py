from datetime import datetime

from odoo import http
from odoo.http import request


class DiscussController(http.Controller):
    @http.route('/mail/rtc/session/welcomepage', type="json", auth='public')
    def session_send_welcomepage(self, channel_id, values):
        channel_sudo = request.env['mail.channel'].sudo(). \
            browse(int(channel_id)).exists()
        if channel_sudo:
            channel_sudo._add_userid(values)
            if not channel_sudo.is_lockmeet:
                if not channel_sudo.is_lockpassword:
                    return True
                if channel_sudo.is_password == values['password']:
                    return True
                else:
                    return 'incorrect-password'
            else:
                return 'lock-meeting'

    @http.route('/mail/rtc/session/lock-meeting', type="json", auth='public')
    def session_send_discusspage(self, channel_id, values):
        channel_sudo = request.env['mail.channel'].sudo().\
            browse(int(channel_id)).exists()
        if channel_sudo:
            channel_sudo._update_lockmeet(values)

    @http.route('/mail/rtc/session/lock-password', type="json", auth='public')
    def session_lock_meeting(self, channel_id, values):
        channel_sudo = request.env['mail.channel'].sudo().\
            browse(int(channel_id)).exists()
        if channel_sudo:
            channel_sudo._update_lockpassword(values)

    @http.route('/mail/rtc/session/check-lock', type="json", auth='public')
    def session_check_lock_passowrd(self, channel_id):
        channel_sudo = request.env['mail.channel'].sudo().\
            browse(int(channel_id)).exists()
        if channel_sudo.is_lockpassword:
            return True
        else:
            return False

    @http.route('/mail/rtc/session/create-password', type="json", auth='public')
    def session_create_password(self, channel_id):
        channel_sudo = request.env['mail.channel'].sudo().\
            browse(int(channel_id)).exists()
        if channel_sudo:
            channel_sudo._create_password()
            calendar_event = request.env['calendar.event'].sudo().create({
                'name': "meeting" + str(channel_id),
                'is_password': channel_sudo.is_password,
                'start': datetime.now(), 'stop': datetime.now()})
            url = str(calendar_event.get_base_url())+'/chat/' + \
                str(channel_sudo.id)+'/'+str(channel_sudo.uuid)
            calendar_event.videocall_location = url
            calendar_event.is_meeting = True
            calendar_event.channel_id = channel_sudo
            request.env['mail.channel'].sudo().browse(int(channel_id)).write(
                {'calendar_id': int(calendar_event.id)})
            # Todo: Fix Who Should Be Host
            # channel_sudo.channel_last_seen_partner_ids.is_host = True
            return {'password': channel_sudo.is_password, 'calendar': calendar_event.id}

    @http.route('/mail/rtc/session/get-password', type="json", auth='public')
    def session_send_password(self, channel_id):
        channel_sudo = request.env['mail.channel'].sudo().\
            browse(int(channel_id)).exists()
        if channel_sudo:
            return channel_sudo.is_password

    @http.route('/mail/rtc/session/update-and-emoji',
                methods=['POST'], type="json", auth='public')
    def session_update_and_emoji(self, session_id, values):
        session = request.env['mail.channel.rtc.session'].sudo().\
            browse(int(session_id)).exists()
        session.update_and_emoji(values, int(session_id))

    @http.route('/mail/rtc/session/temp-host', methods=['POST'],
                type="json", auth='user')
    def channel_call_join_host(self, channel_id, partner=None):
        channel = request.env['mail.channel'].sudo().browse(
            int(channel_id)).exists()

        channel_partner = request.env['mail.channel.member'].sudo().search(
            [('channel_id', '=', channel.id), ('partner_id', '=', int(partner))])
        if channel_partner:
            return channel_partner.is_host
