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

class CalendarAlarm(models.Model):
    _inherit = "calendar.alarm"

    @api.depends('alarm_type', 'mail_template_id')
    def _compute_mail_template_id(self):
        for alarm in self:
            if alarm.alarm_type == 'email' and not alarm.mail_template_id:
                alarm.mail_template_id = self.env['ir.model.data']._xmlid_to_res_id('isep_appointments.calendar_template_meeting_reminder')
            elif alarm.alarm_type != 'email' or not alarm.mail_template_id:
                alarm.mail_template_id = False
