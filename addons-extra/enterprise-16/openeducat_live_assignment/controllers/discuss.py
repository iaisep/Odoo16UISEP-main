# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class DiscussController(http.Controller):
    @http.route('/mail/rtc/session/add-assignment', type="json", auth='user')
    def session_assignment(self, channel_id):
        channel_sudo = request.env['mail.channel'].\
            browse(int(channel_id)).sudo().exists()
        if channel_sudo:
            if channel_sudo.calendar_id:
                calender_event = request.env['calendar.event'].sudo().browse(
                    int(channel_sudo.calendar_id)).exists()
                return {'course': calender_event.course_id.id,
                        'subject': calender_event.subject_id.id,
                        'batch': calender_event.batch_id.id}
