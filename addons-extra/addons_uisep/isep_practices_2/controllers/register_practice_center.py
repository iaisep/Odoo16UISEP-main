# -*- coding: utf-8 -*-
import logging

import odoo.http
from odoo import http
from odoo.http import request
from odoo.tools import json
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
import io
from werkzeug.utils import redirect
_logger = logging.getLogger(__name__)


class PracticeCenterPortal(http.Controller):

    def time_to_float(self, time_str):
        """Convierte una hora en formato HH:MM a un número decimal"""
        if time_str:
            try:
                hours, minutes = map(int, time_str.split(":"))
                return hours + (minutes / 60)
            except ValueError:
                # _logger.error(f"Formato de hora incorrecto: {time_str}")
                return 0.0  # En caso de error, se devuelve 0.0
        return 0.0


    @http.route('/my/register_practice_center', type='http', auth='public', website=True)
    def register_practice_center(self, **kwargs):

        if kwargs.get('name') and kwargs.get('email'):
            type_ids = []
            index = 0


            while f'type_ids[{index}][type_of_practice]' in kwargs:


                type_of_practice = kwargs.get(f'type_ids[{index}][type_of_practice]')
                description = kwargs.get(f'type_ids[{index}][description]')

                if type_of_practice:

                    type_of_practice = request.env['practice.center.type'].search([('type_of_practice', '=', type_of_practice)])
                    type_ids.append(type_of_practice.id)

                index += 1


            practice_center = request.env['practice.center'].sudo().create({
                'name': kwargs.get('name'),
                'coordinator': kwargs.get('coordinator'),
                'official_name': kwargs.get('official_name'),
                'signatory_name': kwargs.get('signatory_name'),
                'email': kwargs.get('email'),
                # 'phone': kwargs.get('phone'),
                'mobil': kwargs.get('mobil'),
                'number_places': kwargs.get('number_places'),
                'street': kwargs.get('street'),
                'country_id': int(kwargs.get('country_id')) if kwargs.get('country_id') else False,
                'state_id': int(kwargs.get('state_id')) if kwargs.get('state_id') else False,
                # 'zip_id': int(kwargs.get('zip_id')) if kwargs.get('zip_id') else False,
                'postal_code': kwargs.get('postal_code'),
                'schedule_description': kwargs.get('schedule_description'),
                'type_ids': type_ids,
                # '_fa': 'fa-file-o',
            })

            # Procesar horarios de práctica
            schedule_index = 0
            schedule_ids = []
            while f'schedule_ids[{schedule_index}][shift_id]' in kwargs:
                shift_id = kwargs.get(f'schedule_ids[{schedule_index}][shift_id]')
                day_of_week_id = kwargs.get(f'schedule_ids[{schedule_index}][day_of_week_id]')
                start_time_str = kwargs.get(f'schedule_ids[{schedule_index}][start_time]')
                end_time_str = kwargs.get(f'schedule_ids[{schedule_index}][end_time]')
                description = kwargs.get(f'schedule_ids[{schedule_index}][description]', '')

                # 🔄 Convertir a formato decimal
                start_time = self.time_to_float(start_time_str)
                end_time = self.time_to_float(end_time_str)

                if shift_id and day_of_week_id and start_time and end_time:
                    schedule = request.env['practice.center.schedule'].sudo().create({
                        'center_id': practice_center.id,
                        'shift_id': shift_id,
                        'day_of_week_id': day_of_week_id,
                        'start_time': start_time,
                        'end_time': end_time,
                        'description': description,
                    })

                    # _logger.info(f"Horario guardado - Shift: {shift_id}, Day: {day_of_week_id}, Start: {start_time}, End: {end_time}")
                    # schedule_ids.append(schedule.id)
                else:
                    _logger.info("No se crea")

                schedule_index += 1

            return request.render('isep_practices_2.success_page', {})


        # Cargar los datos para la vista del portal
        shifts = request.env['practice.center.shift'].sudo().search([])
        days = request.env['practice.center.day'].sudo().search([])

        return request.render('isep_practices_2.register_practice_center', {            
            'shifts': shifts,
            'days': days})