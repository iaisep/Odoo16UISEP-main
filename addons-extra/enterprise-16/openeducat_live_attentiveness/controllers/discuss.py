# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_live.controllers.discuss import DiscussController


class DiscussController(DiscussController):

    @http.route()
    def session_send_welcomepage(self, channel_id, values):
        partner = None
        channel_sudo = request.env['mail.channel']. \
            browse(int(channel_id)).sudo().exists()
        if channel_sudo:
            channel_sudo._add_userid(values)
            if not channel_sudo.is_lockmeet:
                if values['partner_id']:
                    partner = request.env['res.partner'].sudo().browse(
                        int(values['partner_id']))
                if partner and channel_sudo.calendar_id:
                    current_time = datetime.now()
                    calender_id = request.env['calendar.event'].sudo(). \
                        browse(channel_sudo.calendar_id)
                    log_data = {
                        'partner_id': int(partner.id),
                        'join_time': current_time,
                        'meeting_id': calender_id.id
                    }
                    channel_log = request.env['channel.logs'].sudo().search(
                        [('meeting_id', '=', calender_id.id),
                         ('partner_id', '=', int(partner.id))])
                    if not channel_log:
                        channel_log = request.env['channel.logs']. \
                            sudo().create(log_data)

        res = super(DiscussController, self).session_send_welcomepage(
            channel_id, values)
        return res

    @http.route('/mail/rtc/session/is-start-time', type="json", auth='public')
    def session_start_time(self, channel_id, partner_id, calendar_id):
        start_time = datetime.now()
        channel_sudo = request.env['mail.channel'].browse(
            int(channel_id)).sudo().exists()
        channel_log = request.env['channel.logs'].sudo().search(
            [('meeting_id', '=', channel_sudo.calendar_id),
             ('partner_id', '=', partner_id)])
        if channel_log:
            log_id = request.env['log.attentive'].sudo(). \
                search([('logs_id', '=', int(channel_log.id))])

            if log_id:
                for record in log_id:
                    end_time = record.end_time
                if end_time:
                    log_id = request.env['log.attentive'].sudo().create(
                        {'start_time': start_time, 'logs_id': channel_log.id})
                    return log_id.id
            else:
                log_id = request.env['log.attentive'].sudo().create(
                    {'start_time': start_time, 'logs_id': channel_log.id})
                return log_id.id

    @http.route('/mail/rtc/session/is-end-time', type="json", auth='public')
    def session_end_time(self, log_id, channel_id):
        channel_sudo = request.env['mail.channel']. \
            browse(int(channel_id)).sudo().exists()
        if channel_sudo.is_EndMeet:
            if log_id:
                log_id = request.env['log.attentive'].sudo(). \
                    browse(int(log_id)).write(
                    {'end_time': datetime.now()})

    @http.route('/mail/rtc/session/raisedhand', type="json", auth='public')
    def session_raishand(self, channel_id, partner_id, session_id):
        vals = {}
        fields = {'id': True,
                  'channelMember': {
                      'id': True, 'channel': {},
                      'persona': {
                          'partner': {
                              'id',
                              'name',
                              'im_status'},
                          'guest': {
                              'id',
                              'name',
                              'im_status'
                          }}},
                  'isCameraOn': True,
                  'isDeaf': True,
                  'isSelfMuted': True,
                  'isScreenSharingOn': True}
        channel_sudo = request.env['mail.channel'].browse(
            int(channel_id)).sudo().exists()
        session = request.env['mail.channel.rtc.session'].sudo(). \
            browse(int(session_id)).exists()
        vals['channelMember'] = session.channel_member_id. \
            _mail_channel_member_format(fields=fields.get('channelMember')). \
            get(session.channel_member_id)
        if 'partner' in vals['channelMember']['persona']:
            channel_log = request.env['channel.logs'].sudo().search(
                [('meeting_id', '=', channel_sudo.calendar_id),
                 ('partner_id', '=',
                  int(vals['channelMember']['persona']['partner']['id']))])
            if channel_sudo.is_EndMeet:
                channel_log.raised_hand = channel_log.raised_hand + 1

    @http.route('/mail/rtc/session/add-guest', type="json", auth='public')
    def session_add_guest(self, guest, calendar_id):
        for record in guest:
            if record != 'Anonymous':
                guests = request.env['meeting.guest'].sudo().search(
                    [('guest', '=', record), ('meetin_guest_id', "=", calendar_id)])
                if not guests:
                    request.env['meeting.guest'].sudo().create(
                        {'guest': record, 'meetin_guest_id': calendar_id})

    @http.route('/mail/rtc/session/start-end-meeting', type="json", auth='public')
    def session_create_meeting(self, channel_id, meeting, host):
        if meeting == 'end':
            channel_sudo = request.env['mail.channel']. \
                browse(int(channel_id)).sudo().exists()
            if host:
                if channel_sudo:
                    calender_event = request.env['calendar.event'].sudo(). \
                        browse(channel_sudo.calendar_id)
                    calender_event.write({'stop': datetime.now()})
                    calender_event.write({
                        'meeting_start_time': calender_event.start,
                        'meeting_end_time': datetime.now(),
                        'total_student': len(calender_event.logs_line),
                        'total_guest': len(calender_event.guest_line),
                        'total_member':
                            len(calender_event.guest_line) +
                            len(calender_event.logs_line),
                        'meeting_duration': calender_event.duration,
                    })
                    calender_event._compute_total_percentage()
                    channel_sudo.is_EndMeet = False
        return True
