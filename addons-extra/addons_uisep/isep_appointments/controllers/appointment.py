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
import json
import pytz

from odoo import api, fields, models
from odoo.http import request, route
from datetime import datetime, timedelta
from odoo.addons.appointment.controllers.appointment import AppointmentController
from odoo.addons.appointment.controllers.calendar import AppointmentCalendarController
from odoo.osv import expression

class AppointmentController(AppointmentController):

    @classmethod
    def _appointments_base_domain(cls, filter_appointment_type_ids, search=False, invite_token=False):
        res = super()._appointments_base_domain(filter_appointment_type_ids, search=search, invite_token=invite_token)
        if not request.env.user.has_group('base.group_user'):
            res = expression.AND([res, [('is_private_appo','=',False)]])
        return res

    def _prepare_appointment_type_page_values(self, appointment_type, staff_user_id=False, **kwargs):
        res = super()._prepare_appointment_type_page_values(appointment_type, staff_user_id=staff_user_id, **kwargs)
        partner = request.env.user.partner_id
        student = request.env['op.student'].sudo().search([('partner_id', '=', partner.id)])
        # Tymezone to see tymezone actual
        timezone = request.session.get('timezone')
        show_calendar = True

        if not timezone:
            timezone = request.env.context.get('tz') or 'UTC'
            request.session['timezone'] = timezone
        tz_session = pytz.timezone(timezone)

        # Get actual date in UTC and convert in timezone
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        now_local = now_utc.astimezone(tz_session)

        #import pdb;pdb.set_trace()
        if student:
            penalization_line_id = request.env['appointment.penalization.line'].sudo().search([('user_id', '=', request.env.user.id)],limit=1)

            if penalization_line_id and penalization_line_id.next_date_book:
                if penalization_line_id.next_date_book.tzinfo is None:
                    next_date_book = penalization_line_id.next_date_book.replace(tzinfo=pytz.utc).astimezone(tz_session)
                else:
                    next_date_book = penalization_line_id.next_date_book.astimezone(tz_session)

                if next_date_book > now_local:
                    show_calendar = False
                else:
                    show_calendar = True

                res.update({'next_date_book': penalization_line_id.next_date_book})
            else:
                show_calendar = True

        res.update({'show_calendar': show_calendar})
        return res


class AppointmentCalendarController(AppointmentCalendarController):

    @route(['/calendar/view/<string:access_token>'], type='http', auth="public", website=True)
    def appointment_view(self, access_token, partner_id, state=False, **kwargs):
        res = super(AppointmentCalendarController,self).appointment_view(access_token, partner_id, state=state, **kwargs)
        event = request.env['calendar.event'].sudo().search([('access_token', '=', access_token)], limit=1)
        partner = request.env.user.partner_id
        student = request.env['op.student'].sudo().search([('partner_id', '=', partner.id)])
        attendee_id = attended_partner_id = request.env['calendar.attendee'].sudo().search([('partner_id','=',request.env.user.partner_id.id),('event_id','=',event.id)])

        #Tymezone to see tymezone actual
        timezone = request.session.get('timezone')
        if not timezone:
            timezone = request.env.context.get(
                'tz') or event.appointment_type_id.appointment_tz or event.partner_ids and event.partner_ids[
                           0].tz or event.user_id.tz or 'UTC'
            request.session['timezone'] = timezone
        tz_session = pytz.timezone(timezone)

        #Get actual date in UTC and convert in timezone
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        now_local = now_utc.astimezone(tz_session)
        #Convert the time of start event in datetime with timezone
        event_start = fields.Datetime.from_string(res.qcontext.get('event').start).replace(tzinfo=pytz.utc).astimezone(tz_session)

        #Get diference in minutes
        minutes_diff = (event_start - now_local).total_seconds() / 60.0

        #Search res_condig min
        isp_time_before_reunion = int(request.env['ir.config_parameter'].sudo().get_param('isep_appointments.isp_time_before_reunion', default=0))
        isp_time_after_reunion = int(request.env['ir.config_parameter'].sudo().get_param('isep_appointments.isp_time_after_reunion', default=0))

        #Get Limit
        #Flag if time is 15
        if 0 <= minutes_diff <= isp_time_before_reunion:
            is_soon = True
        elif -isp_time_after_reunion <= minutes_diff < 0:
            is_soon = True
        else:
            is_soon = False
        res.qcontext.update({'is_student': True if student else False,'is_soon':is_soon,'is_attend':True if attendee_id and attendee_id.is_attend else False})
        return res

    # @route(['/calendar/view/<string:access_token>'], type='http', auth="public", website=True)
    # def appointment_view(self, access_token, partner_id, state=False, **kwargs):
    #     """
    #     Render the validation of an appointment and display a summary of it
    #
    #     :param access_token: the access_token of the event linked to the appointment
    #     :param state: allow to display an info message, possible values:
    #         - new: Info message displayed when the appointment has been correctly created
    #         - no-cancel: Info message displayed when an appointment can no longer be canceled
    #     """
    #     event = request.env['calendar.event'].sudo().search([('access_token', '=', access_token)], limit=1)
    #     if not event:
    #         return request.not_found()
    #     timezone = request.session.get('timezone')
    #     if not timezone:
    #         timezone = request.env.context.get(
    #             'tz') or event.appointment_type_id.appointment_tz or event.partner_ids and event.partner_ids[
    #                        0].tz or event.user_id.tz or 'UTC'
    #         request.session['timezone'] = timezone
    #     tz_session = pytz.timezone(timezone)
    #
    #     date_start_suffix = ""
    #     format_func = format_datetime
    #     if not event.allday:
    #         url_date_start = fields.Datetime.from_string(event.start).strftime('%Y%m%dT%H%M%SZ')
    #         url_date_stop = fields.Datetime.from_string(event.stop).strftime('%Y%m%dT%H%M%SZ')
    #         date_start = fields.Datetime.from_string(event.start).replace(tzinfo=pytz.utc).astimezone(tz_session)
    #     else:
    #         url_date_start = url_date_stop = fields.Date.from_string(event.start_date).strftime('%Y%m%d')
    #         date_start = fields.Date.from_string(event.start_date)
    #         format_func = format_date
    #         date_start_suffix = _(', All Day')
    #
    #     locale = get_lang(request.env).code
    #     day_name = format_func(date_start, 'EEE', locale=locale)
    #     date_start = day_name + ' ' + format_func(date_start, locale=locale) + date_start_suffix
    #     # convert_online_event_desc_to_text method for correct data formatting in external calendars
    #     details = event.appointment_type_id and event.appointment_type_id.message_confirmation or event.convert_online_event_desc_to_text(
    #         event.description) or ''
    #     params = {
    #         'action': 'TEMPLATE',
    #         'text': event.name,
    #         'dates': url_date_start + '/' + url_date_stop,
    #         'details': html2plaintext(details.encode('utf-8'))
    #     }
    #     if event.location:
    #         params.update(location=event.location.replace('\n', ' '))
    #     encoded_params = url_encode(params)
    #     google_url = 'https://www.google.com/calendar/render?' + encoded_params
    #
    #     return request.render("appointment.appointment_validated", {
    #         'event': event,
    #         'datetime_start': date_start,
    #         'google_url': google_url,
    #         'state': state,
    #         'partner_id': partner_id,
    #         'is_html_empty': is_html_empty,
    #     })