# -*- coding: utf-8 -*-
import pprint

from odoo import http
from odoo.http import request
from odoo.tools import json
from odoo.addons.portal.controllers.portal import CustomerPortal


class TessisreviewwPortal(http.Controller):

    @http.route(['/my/tesis_models/new'], type='http', auth='user', website=True, csrf=False)
    def create_tesis_model(self, **kwargs):
        """
        Página para crear una nueva solicitud.
        """




        if request.httprequest.method == 'POST':
            # Capturar datos del formulario
            name = kwargs.get('student_name')
            email = kwargs.get('student_email')
            course_id = kwargs.get('course_id')
            application_description = kwargs.get('application_description')
            type_tesis = kwargs.get('type_tesis')
  



            # Función para convertir cadenas vacías a 0.0
            def safe_float(value):
                try:
                    return float(value) if value else 0.0
                except ValueError:
                    return 0.0


            # Verificar si ya existe una solicitud en proceso para este usuario
            user_id = request.env.user.id
            tesis_model_id = request.env['tesis.model'].sudo().search([
                ('email', '=', email),
                ('course_id', '=', int(course_id)),
            ], limit=1)


            if tesis_model_id:
                # Mostrar mensaje de error en lugar de crear una nueva solicitud
                return request.render('isep_tesis_model.tesis_model_form_template', {
                    'error_message': 'Ya tienes una Revision de tesis con este curso en proceso. Espera hasta que finalize.',
                    'courses': request.env['op.student.course'].sudo().search([('student_id', '=',
                                                                                request.env['op.student'].sudo().search(
                                                                                    [('user_id', '=', user_id)],
                                                                                    limit=1).id)]),
                    'student': request.env['op.student'].sudo().search([('user_id', '=', user_id)], limit=1),
                })

            # Crear registro en el modelo
            values = {
                'name': name,
                'email': email,
                'course_id': int(course_id),
                'type_thesis': type_tesis,
                'application_description': application_description,
              
            }
            pprint.pprint(values)
            rst = request.env['tesis.model'].sudo().create(values)
            return request.redirect('/my/tesis_models2')

        # Cargar datos para el formulario
        error_message=""
        user_id = request.env.user.id
        student = request.env['op.student'].sudo().search([('user_id', '=', user_id)], limit=1)
        courses = request.env['op.student.course'].sudo().search([('student_id', '=', student.id)])

        values={
            'courses': courses,
            'student': student,
            'error_message': error_message,
        }

        return request.render('isep_tesis_model.tesis_model_form_template', values)

