# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json
from datetime import datetime, timedelta

import pymsteams
import requests
from pytz import timezone

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TeamsMeet(models.TransientModel):

    _name = 'msteams.meeting'
    _description = 'Microsoft Teams Meetings'

    subject = fields.Char(required=True)
    invite_via_email = fields.Boolean()
    start_date = fields.Datetime(required=True, string="Start time")
    end_date = fields.Datetime(required=True, string="End time")
    meeting_id = fields.Many2one('calendar.event')

    @api.model
    def default_get(self, fields):
        res = super(TeamsMeet, self).default_get(fields)
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        calender = self.env['calendar.event'].browse(active_id)
        res.update({
            'meeting_id': active_id,
            'subject': calender.name,
            'start_date': calender.start,
            'end_date': calender.stop,
            'invite_via_email': True,
        })
        return res

    def create_meeting(self):
        timez = str(self.env.user.tz)
        res_config = self.env['ir.config_parameter'].sudo()
        res_config_settings = self.env['res.config.settings'].sudo()
        res_config_settings.do_refresh_token()
        for res in self: # noqa
            webhook_url_key = res_config.search([('key', '=', 'webhook.url')])
            access_token_key = res_config.search(
                [('key', '=', 'access.token')])
            send_card_key = res_config.search([['key', '=', 'ms.send.card']])
            course_send_card_key = res_config.search(
                [['key', '=', 'course.send.card']])
            webhook_url = webhook_url_key.value
            access_token = access_token_key.value
            send_card = send_card_key.value
            course_send_card = course_send_card_key.value

        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        calendar = self.env['calendar.event'].browse(active_id)
        calendar.start_date = self.start_date
        calendar.online_meeting = True

        for record in self:
            for attendee in self.meeting_id.attendee_ids:
                if record.meeting_id.user_id.partner_id == attendee.partner_id:
                    if record.meeting_id.user_id.tz:
                        timez = str(record.meeting_id.user_id.tz)
                    else:
                        raise ValidationError(
                            _("Timezone for user '{}' is not configured.".format(
                                record.meeting_id.user_id.name)))

        start_time = 'T'.join(str(self.start_date.astimezone(
            timezone(timez))).split(' '))

        if self.end_date:
            end_time = 'T'.join(str(self.end_date.astimezone(
                timezone(timez))).split(' '))
        else:

            time = str(datetime.strptime(
                str(self.start_date), '%Y-%m-%d %H:%M:%S') + timedelta(minutes=30))
            end_time = 'T'.join(time.split(' ')) + 'Z'

        url = 'https://graph.microsoft.com/v1.0/me/onlineMeetings'

        data = {"subject": self.subject,
                "startDateTime": start_time,
                "endDateTime": end_time,
                }

        headers = {"Authorization": access_token,
                   'Content-type': 	'application/json'}

        user_response_data = requests.post(
            url, headers=headers, data=json.dumps(data))

        json_data = user_response_data.json()
        if 'joinWebUrl' not in json_data:
            raise ValidationError(
                _("Token expired. Please refresh the token"))

        else:
            myTeamsMessage = None
            calendar.meet_url = json_data['joinWebUrl']

            if send_card == 'True':
                myTeamsMessage = pymsteams.connectorcard(webhook_url)

            elif course_send_card == 'True':
                if calendar.op_session_id.subject_id.webhook_url:
                    myTeamsMessage = pymsteams.connectorcard(
                        calendar.op_session_id.subject_id.webhook_url)
                else:
                    myTeamsMessage = pymsteams.connectorcard(
                        calendar.op_session_id.course_id.webhook_url)

            if myTeamsMessage:
                myTeamsMessage.title(self.subject)

                section1 = pymsteams.cardsection()
                section2 = pymsteams.cardsection()
                section3 = pymsteams.cardsection()

                if calendar.description:
                    myTeamsMessage.text("{}".format(calendar.description))
                else:
                    myTeamsMessage.text("{} invited for a meeting.".format(
                        calendar.user_id.partner_id.name))

                section1.text("Start time: {}".format(
                    str(self.start_date.astimezone(timezone(timez)))[:-6]))
                section2.text("End time: {}".format(
                    str(self.end_date.astimezone(timezone(timez)))[:-6]))
                section3.text("Duration: {} hr".format(calendar.duration))

                myTeamsMessage.addSection(section1)
                myTeamsMessage.addSection(section2)
                myTeamsMessage.addSection(section3)

                myTeamsMessage.addLinkButton(
                    "Join Meeting", json_data['joinWebUrl'])
                myTeamsMessage.send()

            for record in self:
                for attendee in self.meeting_id.attendee_ids:
                    if record.meeting_id.user_id.partner_id == attendee.partner_id:
                        attendee.write({
                            'attendee_meeting_url': json_data['joinWebUrl'],
                        })
                    else:
                        attendee.write({
                            'attendee_meeting_url': json_data['joinWebUrl'],
                        })
                if record.invite_via_email is True:
                    record.meeting_id.action_sendmail()
                return True


class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    meet_url = fields.Char(string="Teams Meeting URL", readonly=True)
    online_meeting = fields.Boolean()
