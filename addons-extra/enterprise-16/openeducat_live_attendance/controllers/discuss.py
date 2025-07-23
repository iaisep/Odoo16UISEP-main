# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_live.controllers.discuss import DiscussController


class DiscussController(DiscussController):

    @http.route()
    def session_send_welcomepage(self, channel_id, values):
        channel_sudo = request.env['mail.channel'].\
            browse(int(channel_id)).sudo().exists()
        if channel_sudo:
            channel_sudo._add_userid(values)
            if not channel_sudo.is_lockmeet:
                student = request.env['op.student'].sudo().search([
                    ('user_id', '=', channel_sudo.users_id)])
                if student and channel_sudo.sheet_id:
                    vals = {
                        'student_id': student.id,
                        'attendance_id': channel_sudo.sheet_id,
                    }
                    attendance_line = request.env['op.attendance.line']. \
                        sudo().search([('student_id', '=', student.id),
                                       ('attendance_id', '=',
                                        channel_sudo.sheet_id)])
                    if not attendance_line:
                        attendance_line = request.env['op.attendance.line']. \
                            sudo().create(vals)
        res = super(DiscussController, self).session_send_welcomepage(
            channel_id, values)
        return res

    @http.route('/mail/rtc/session/get-registerdata', type="json", auth='user')
    def session_send_registerdata(self):
        attendance = request.env['op.attendance.register']. \
            sudo().search_read([], ['name'])
        return attendance

    @http.route('/mail/rtc/session/get-sheetdata', type="json", auth='user')
    def session_send_sheetdata(self, values):
        today_date = date.today()
        if 'registerid' in values:
            register_data = request.env['op.attendance.register'].sudo().\
                browse(int(values['registerid']))
            sheet = request.env['op.attendance.sheet']. \
                sudo().search_read([('register_id', '=', register_data.id),
                                    ('attendance_date', '=', today_date)],
                                   ['attendance_sheet_date'])
            return sheet

    @http.route('/mail/rtc/session/get-sheetid', type="json", auth='user')
    def session_send_sheetid(self, values, channel_id):
        if 'registerid' in values:
            register_data = request.env['op.attendance.register'].sudo().\
                browse(int(values['registerid']))
            if register_data:
                sheet = request.env['op.attendance.sheet'].sudo().create({
                    'register_id': register_data.id
                })
                channel_sudo = request.env['mail.channel'].browse(channel_id).\
                    sudo().exists()
                if channel_sudo:
                    channel_sudo._add_sheetid(sheet.id)

    @http.route('/mail/rtc/session/add-sheetid', type="json", auth='user')
    def session_send_existing_sheetid(self, values, channel_id):
        channel_sudo = request.env['mail.channel'].browse(channel_id).\
            sudo().exists()
        if channel_sudo:
            channel_sudo._add_sheetid(int(values['sheetid']))
