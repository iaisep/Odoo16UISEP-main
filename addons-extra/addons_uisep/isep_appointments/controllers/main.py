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
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from datetime import datetime, timedelta

class AttendedLists(http.Controller):

    @http.route('/appointment/assists/meeting/<model("calendar.event"):event>',type='http', auth="user", methods=['POST'], website=True)
    def assistMeeting(self,event=False):
        attended_partner_id = request.env['calendar.attendee'].sudo().search([('partner_id','=',request.env.user.partner_id.id),('event_id','=',event.id)])
        if attended_partner_id:
            attended_partner_id.sudo().write({'is_attend':True})
            penalization_line_id = request.env['appointment.penalization.line'].sudo().search([('user_id','=',request.env.user.id)])
            # if penalization_line_id:
            #     penalization_line_id.sudo().write({'penalization_id':False,
            #                                        #'total_absence':0,
            #                                        'next_date_book':False,
            #                                        'datetime_create':datetime.now()})
        return request.redirect(f"/calendar/view/{event.access_token}?partner_id={request.env.user.partner_id.id}")


