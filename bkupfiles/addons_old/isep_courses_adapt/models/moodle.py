# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
import requests


class MoodleCredential(models.Model):
    _name = "moodle.credential"

    access_token = fields.Char(string="Access Token")
    request_url = fields.Char(string="Request URL")
    company_ids=fields.Many2many("res.company",string="Compañias")
    moodle_modules_ids=fields.One2many("moodle.modules.default","moodle_id",string="Modulos Moodle")

    def connect(self,function,params):
        url = self.request_url + "/webservice/rest/server.php"

        #raise UserError( str( url))
        params.update({
            'wstoken': self.access_token,
            'moodlewsrestformat': 'json',
            'wsfunction': function
        })
        try:
            response = requests.post(url, params)
        except Exception as e:
            raise UserError(str(e))
        source = response.json()
        if type(source) == dict and source.get('exception'):
            raise ValidationError(("Moodle error: {}".format(source.get('message'))))
        elif response.status_code == 404:
            raise ValidationError(_("Moodle error: failed connection"))
        else:
            return source
            
    def moodle_function(self, function: str, params: dict) -> dict:
        return self.connect(function, params)

    def get_users_by_field(self, field: str, dni: str) -> dict:
        function = "core_user_get_users_by_field"
        params = {'field': field, 'values[0]': dni}
        return self.connect(function, params)

    def get_course_by_field(self, field: str, value) -> dict:
        function = "core_course_get_courses_by_field"
        params = {
            'field': field,
            'value': value
        }
        return self.connect(function, params)

    def get_user_by_field(self, field: str, value: str) -> dict:
        function = "core_user_get_users_by_field"
        params = {'field': field, 'values[0]': value}
        users = self.connect(function, params)
        user = None
        if len(users) > 0:
            user = users[0]
        return user

    def get_users_courses(self, user_id: int) -> dict:
        """
        Funcion para extraer todos los cursos en la que se encuentra inscrito un usuario

        core_enrol_get_users_courses

        params = {
            'userid': user_id
        }

        :param user_id: int id del usuario
        :return: dict diccionario con el resultado 
        """
        function = "core_enrol_get_users_courses"
        params = {
            'userid': user_id
        }
        return self.connect(function, params)

    def get_group(self, course_id: int, group_id: str) -> dict:
        """
        Obtiene el grupo de un curso en base al id del curso y del grupo 

        core_group_get_course_groups

        :param course_id: int id del curso en moodle
        :param group_id: str id del grupo en moodle
        :return: dict returna un diccionario con el resultado
        """
        function = "core_group_get_course_groups"
        params = {'courseid': course_id}
        groups = self.connect(function, params)
        group = None
        for row in groups:
            if row["name"] == group_id:
                group = row
        return group
        
    def core_group_create_groups(self, name: str, course_id: int) -> dict:
        """
        Crea un grupo en base al id de un curso 
        params = {
            'groups[0][description]': name,
            'groups[0][name]': name,
            'groups[0][courseid]': course_id,
        }

        :param name: str  nombre del nuevo grupo
        :param course_id: int id del curso 
        :return: dict retorna un diccionario con los valores
        """
        params = {
            'groups[0][description]': name,
            'groups[0][name]': name,
            'groups[0][courseid]': course_id,
        }
        function = "core_group_create_groups"
        return self.connect(function, params)

    def enrol_user(self, course_id: str, user_id: int) -> dict:
        """
        Funcion para la matriculacion en moodle

        enrol_manual_enrol_users

        params = {
            'enrolments[0][courseid]': course_id,
            'enrolments[0][userid]': user_id,
            'enrolments[0][roleid]': 5
        }
        :param course_id: str id del curso
        :param user_id: int id del usuario
        :param roleid: int id del role del usuario por defecto 5 que es estudiante
        :return: dict
        """
        function = "enrol_manual_enrol_users"
        params = {
            'enrolments[0][courseid]': course_id,
            'enrolments[0][userid]': user_id,
            'enrolments[0][roleid]': 5
        }
        return self.connect(function, params)

    def add_group_members(self, group_id: int, user_id: int) -> dict:
        """
        Funcion para matricular al usuario a un grupo 

        core_group_add_group_members

        params = {
            'members[0][groupid]': group_id,
            'members[0][userid]': user_id
        }

        :param group_id: int id del grupo
        :param user_id: int id del usuario
        :return: dict
        """
        function = "core_group_add_group_members"
        params = {
            'members[0][groupid]': group_id,
            'members[0][userid]': user_id
        }
        return self.connect(function, params)

class MoodleModulosDefault(models.Model):
    _name = "moodle.modules.default"

    moodle_id=fields.Many2one("moodle.credential",string=" Instancia ID")
    area_id=fields.Many2one("op.category",string=" Instancia ID")
    name=fields.Char(string="Modulo")
    number_id=fields.Char(string="Number ID")
    moodle_category=fields.Char(string="Moodle Categoria ID")
