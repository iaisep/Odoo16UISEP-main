# -*- coding: utf-8 -*-
import pprint

from odoo import http
from odoo.http import request
from odoo.tools import json
from odoo.addons.portal.controllers.portal import CustomerPortal


class PracticeCenterPortal(http.Controller):

    @http.route(['/my/practice_requests/new'], type='http', auth='user', website=True, csrf=False)
    def create_practice_request(self, **kwargs):
        """
        Página para crear una nueva solicitud.
        """




        if request.httprequest.method == 'POST':
            # Capturar datos del formulario
            name = kwargs.get('student_name')
            email = kwargs.get('student_email')
            course_id = kwargs.get('course_id')
            op_admission_id = kwargs.get('op_admission_id')
            practice_center_type_id = kwargs.get('practice_center_type_id')
            application_description = kwargs.get('application_description')
            # Filtrar y extraer los IDs de los centros seleccionados
            solicited_practice_center_ids = [
                int(key.split('[')[-1].rstrip(']')) for key in kwargs.keys() if key.startswith('center[')
            ]




            # Función para convertir cadenas vacías a 0.0
            def safe_float(value):
                try:
                    return float(value) if value else 0.0
                except ValueError:
                    return 0.0

            # Capturar horarios disponibles de cada día, utilizando safe_float para evitar errores con cadenas vacías
            monday_start_time = safe_float(kwargs.get('monday_available_start_time', ''))
            monday_end_time = safe_float(kwargs.get('monday_available_end_time', ''))

            tuesday_start_time = safe_float(kwargs.get('tuesday_available_start_time', ''))
            tuesday_end_time = safe_float(kwargs.get('tuesday_available_end_time', ''))

            wednesday_start_time = safe_float(kwargs.get('wednesday_available_start_time', ''))
            wednesday_end_time = safe_float(kwargs.get('wednesday_available_end_time', ''))

            thursday_start_time = safe_float(kwargs.get('thursday_available_start_time', ''))
            thursday_end_time = safe_float(kwargs.get('thursday_available_end_time', ''))

            friday_start_time = safe_float(kwargs.get('friday_available_start_time', ''))
            friday_end_time = safe_float(kwargs.get('friday_available_end_time', ''))

            saturday_start_time = safe_float(kwargs.get('saturday_available_start_time', ''))
            saturday_end_time = safe_float(kwargs.get('saturday_available_end_time', ''))

            sunday_start_time = safe_float(kwargs.get('sunday_available_start_time', ''))
            sunday_end_time = safe_float(kwargs.get('sunday_available_end_time', ''))

            # Verificar si ya existe una solicitud en proceso para este usuario
            user_id = request.env.user.id
            practice_request_id = request.env['practice.request'].sudo().search([
                ('user_id', '=', user_id),
                ('course_id', '=', int(course_id)),
            ], limit=1)
            student_id = request.env['op.student'].sudo().search([('user_id', '=', user_id)], limit=1)


            if practice_request_id:
                # Mostrar mensaje de error en lugar de crear una nueva solicitud
                return request.render('isep_practices_2.practice_request_form_template', {
                    'error_message': 'You already have a request in progress. Please wait until it is processed.',
                    'courses': request.env['op.student.course'].sudo().search([('student_id', '=',student_id.id)]),
                    'student': student_id,
                    'practice_types': request.env['practice.center.type'].sudo().search([]),
                    'admissions': request.env['op.admission'].sudo().search([('student_id', '=', student_id.id)])
                })
            if not  solicited_practice_center_ids:
                # Mostrar mensaje de error en lugar de crear una nueva solicitud
                return request.render('isep_practices_2.practice_request_form_template', {
                    'error_message': 'Se requiere elegir el centro de prácticas.',
                    'courses': request.env['op.student.course'].sudo().search([('student_id', '=',student_id.id)]),
                    'student': student_id,
                    'practice_types': request.env['practice.center.type'].sudo().search([]),
                    'admissions': request.env['op.admission'].sudo().search([('student_id', '=', student_id.id)])
                })

            # Crear registro en el modelo
            values = {
                'user_id': user_id,
                'name': name,
                'email': email,
                'course_id': int(course_id),
                'op_admission_id': int(op_admission_id),
                'practice_center_type_id': int(practice_center_type_id),
                'application_description': application_description,
                'country_id': int(kwargs.get('country_id')) if kwargs.get('country_id') else False,
                'state_id': int(kwargs.get('state_id')) if kwargs.get('state_id') else False,
                'zip_id': int(kwargs.get('zip_id')) if kwargs.get('zip_id') else False,

                # Guardar las horas de cada día
                'monday_available_start_time': monday_start_time,
                'monday_available_end_time': monday_end_time,
                'tuesday_available_start_time': tuesday_start_time,
                'tuesday_available_end_time': tuesday_end_time,
                'wednesday_available_start_time': wednesday_start_time,
                'wednesday_available_end_time': wednesday_end_time,
                'thursday_available_start_time': thursday_start_time,
                'thursday_available_end_time': thursday_end_time,
                'friday_available_start_time': friday_start_time,
                'friday_available_end_time': friday_end_time,
                'saturday_available_start_time': saturday_start_time,
                'saturday_available_end_time': saturday_end_time,
                'sunday_available_start_time': sunday_start_time,
                'sunday_available_end_time': sunday_end_time,


            }
            if solicited_practice_center_ids:
                values.update({'solicited_practice_center_ids': [(6, 0, solicited_practice_center_ids)],})
                values.update({'practice_center_id': solicited_practice_center_ids[0]})
            pprint.pprint(values)
            rst = request.env['practice.request'].sudo().create(values)
            return request.redirect('/my/practice_requests2')

        # Cargar datos para el formulario
        error_message=""
        user_id = request.env.user.id
        student = request.env['op.student'].sudo().search([('user_id', '=', user_id)], limit=1)
        courses = request.env['op.student.course'].sudo().search([('student_id', '=', student.id)])
        practice_types = request.env['practice.center.type'].sudo().search([])
        admissions = request.env['op.admission'].sudo().search([('student_id', '=', student.id)])
        values={
            'courses': courses,
            'student': student,
            'admissions': admissions,
            'practice_types': practice_types,
            'error_message': error_message,
        }

        return request.render('isep_practices_2.practice_request_form_template', values)

