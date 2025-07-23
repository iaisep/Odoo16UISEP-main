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
from datetime import date, datetime,timedelta

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    def _create_penalization(self):
        #Fecha y Hora Actual
        now = datetime.now()

        # Search res_condig min
        isp_time_after_reunion = int(
            self.env['ir.config_parameter'].sudo().get_param('isep_appointments.isp_time_after_reunion', default=15))

        # Fecha límite para considerar citas pasadas hace al menos X minutos
        limit_time = now - timedelta(minutes=isp_time_after_reunion)

        #Search Events
        attended_ids = self.env['calendar.attendee'].sudo().search([('event_id.start','<=',limit_time),
                                                                    ('is_attend','=',False),
                                                                    ('is_penalized','=',False),
                                                                    ('event_id.appointment_type_id','!=',False),
                                                                    ('is_student','=',True)])
        if attended_ids:
            for attended in attended_ids:
                #Students
                student_id = self.env['op.student'].sudo().search([('partner_id', '=', attended.partner_id.id)],limit=1)

                #Search Penalization Line
                if student_id:
                    penalization_line_id = self.env['appointment.penalization.line'].search([('user_id','=',student_id.partner_id.user_ids[0].id)])
                    today = datetime.now()
                    total_absence = 1

                    if penalization_line_id:
                        total_absence = penalization_line_id.total_absence + 1
                    else:
                        penalization_line_id = {
                            'datetime_create':datetime.now(),
                            'user_id': student_id.partner_id.user_ids[0].id,
                            'total_absence': total_absence,
                        }

                        #Create Penalization
                        penalization_line_id = self.env['appointment.penalization.line'].create(penalization_line_id)

                    #Update values Penalization
                    penalization_id = self.env['appointment.penalization'].search(
                            [('qty_absence', '<=', total_absence)],
                            order='qty_absence desc', limit=1)

                    # Update penalization line
                    next_date_book = today + timedelta(days=penalization_id.qty_days)

                    #Update Inasistencias
                    penalization_line_id.write({
                        'total_absence': total_absence,
                    })

                    if penalization_id:
                        penalization_line_id.write({'datetime_create': today,
                                                    'penalization_id': penalization_id.id,
                                                    'next_date_book': next_date_book})

                    #Update Attendee details
                    attended.write({
                        'is_penalized':True,
                    })
        return True



