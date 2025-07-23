# -*- coding: utf-8 -*-
#################################################################################
# Author      : ISEP
# Copyright(c): 2016-Present .
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#################################################################################
from odoo import api, fields, models

class CalendarAttendee(models.Model):
    _inherit = "calendar.attendee"

    is_attend = fields.Boolean('Attend?')
    is_penalized = fields.Boolean('Is Penalized?')
    is_student = fields.Boolean('Is Student',compute="_set_is_student",store=True)

    @api.depends('partner_id')
    def _set_is_student(self):
        for record in self:
            # Students
            student_id = self.env['op.student'].sudo().search([('partner_id', '=', record.partner_id.id)], limit=1)
            record.is_student = True if student_id else False

    def _send_mail_to_attendees(self, mail_template, force_send=False):
        mail_template_meeting = self.env.ref('calendar.calendar_template_meeting_invitation')
        if mail_template_meeting == mail_template:
            mail_template = self.env.ref('isep_appointments.calendar_template_meeting_invitation')
        return super(CalendarAttendee,self)._send_mail_to_attendees(mail_template,force_send)