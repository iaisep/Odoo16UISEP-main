# -*- coding: UTF-8 -*-
import json

from odoo.exceptions import UserError
from odoo import _
from requests import post
import logging

logger = logging.getLogger(__name__)
production = True


class MoodleLib:

    def __init__(self, url):

        moodle_user = "Administrador Usuario"
        self.url = "http://localhost/moodle"
        key = "bf3596cf8d02b797bf73436f4ed6bd4a"



        if production:
            moodle_user ="soporte_isep" #"marcadmin" #"webserviceuser"
            self.url = url#"la url se pasa por parametros"

            key ="4ee1b4ee0c79d92dd49c6ec3ffcf90ca"
            if url=="https://campus.universidadeisep.com.br":
                key="7d78379fad1716dafd7903883bce093b"#"2b309d0ed4f69d282931b084b82fceba"
            elif url=="https://campus.universidadisep.com":
                key="2b5bfe2d65f0e1ef4b23c12755a974a1"#"a3236b47c2e6e5102347fa8c6812925b"
            else:
                raise UserError( "Avise al administrador de sistemas"+str(url))
        logger.info("parametros de conexion url: ----- {} token : {}".format(url,key))
        self.conn = self.url
        self.token = key

    def connect(self, function: str, params: dict) -> dict:

        self.url = self.conn + "/webservice/rest/server.php"

        logger.info('****************************************')
        logger.info('*          SECTION PARAMS MOODLE       *')
        logger.info('****************************************')
        logger.info("Url: ----- {}".format(self.url))
        params.update({
            'wstoken': self.token,
            'moodlewsrestformat': 'json',
            'wsfunction': function
        })
        logger.info("Params: ----- {}".format(params))

        response = post(self.url, params)
        source = response.json()
        if type(source) == dict and source.get('exception'):
            logger.info("Params: ----- {}".format(json.dumps(params)))
            logger.info("Moodle response: ----- {}".format(json.dumps(source)))
            raise UserError(
                _("Moodle error: {}".format(source.get('message'))))
        elif response.status_code == 404:
            raise UserError(_("Moodle error: failed connection"))
        else:
            return source

    def moodle_function(self, function: str, params: dict) -> dict:
        return self.connect(function, params)

    def core_course_get_categories(self, key: str, value: str) -> dict:
        
        # Obtiene las categorias segun la clave, valor
        # params = {
        #     'criteria[0][key]': key,
        #     'criteria[0][value]': value
        # }
        # :param key: str es el campo a consultar en el modelo/tabla 
        # :param value: str es el valor de ese campo
        # :return: dict retorna un dictionario con el resultado 
        
        params = {
            'criteria[0][key]': key,
            'criteria[0][value]': value
        }
        function = "core_course_get_categories"
        return self.connect(function, params)

    def create_users(self, firstname: str, lastname: str, dni: str,
                     email: str, password: str) -> dict:
        
        # Funcion para crear usuario en moodle 

        # Function: core_user_create_users

        # user_params = {
        #     'users[0][username]': username.lower(),
        #     'users[0][password]': password,
        #     'users[0][firstname]': firstname,
        #     'users[0][lastname]': lastname,
        #     'users[0][idnumber]': id_number,
        #     'users[0][email]': email
        # }
        # :param password: contraseña
        # :param firstname: str nombre
        # :param lastname: str apellido
        # :param dni: str Documento de indentidad
        # :param email: str correo 
        # :return: dict retorna los elementos creados 
        
        params = {
            'users[0][username]': email.lower(),
            'users[0][password]': password,
            'users[0][firstname]': firstname,
            'users[0][lastname]': lastname,
            'users[0][idnumber]': dni,
            'users[0][email]': email
        }
        function = "core_user_create_users"
        return self.connect(function, params)

    def get_users_by_field(self, field: str, dni: str) -> dict:
    
        # Funcion para obtener el usuario en base al documento de identidad

        # core_user_get_users_by_field, field: idnumber for student

        # :param field: str correo del usuario 
        # :param dni: str documento de identidad
        # :return: dict retorna un diccionario
        
        function = "core_user_get_users_by_field"
        params = {'field': field, 'values[0]': dni}
        return self.connect(function, params)

    def get_user_by_field(self, field: str, value: str) -> dict:
    
        # Obtiene un usuario en base a un campo en especifico 

        # core_user_get_users_by_field, field: idnumber for student

        # :param field: str campo a consultar
        # :param value: str valor del campo
        # :return: dict retorna un diccionario con el resultado
        
        function = "core_user_get_users_by_field"
        params = {'field': field, 'values[0]': value}
        users = self.connect(function, params)
        user = None
        if len(users) > 0:
            user = users[0]
        return user

    def get_course(self, name: str) -> dict:
    
        # Obtiene el curso en base al nombre 
        # core_course_search_courses

        # :param name: str to search nombre del curso a buscar
        # :return: dict of 1 course retorna un diccionario con los valores
        
        function = "core_course_search_courses"
        params = {'criterianame': 'search', 'criteriavalue': name}
        courses = self.connect(function, params)
        course = None
        if courses is not None and courses["total"] > 0:
            course = courses["courses"][0]
        return course

    def get_course_by_field(self, field: str, value) -> dict:
    
        # Obtiene el curso en base a un campo en moodle

        # core_course_get_courses_by_field

        # :param field: str campo a consultar
        # :param value: int,str valor del campo a consultar
        # :return: dict retorna un diccionario con el resultado
        
        function = "core_course_get_courses_by_field"
        params = {
            'field': field,
            'value': value
        }
        print(params)
        return self.connect(function, params)

    def get_group(self, course_id: int, group_id: str) -> dict:
        
        # Obtiene el grupo de un curso en base al id del curso y del grupo 

        # core_group_get_course_groups

        # :param course_id: int id del curso en moodle
        # :param group_id: str id del grupo en moodle
        # :return: dict returna un diccionario con el resultado
        
        function = "core_group_get_course_groups"
        params = {'courseid': course_id}
        groups = self.connect(function, params)
        group = None
        for row in groups:
            if row["name"] == group_id:
                group = row
        return group

    def core_group_create_groups(self, name: str, course_id: int) -> dict:
        
        # Crea un grupo en base al id de un curso 
        # params = {
        #     'groups[0][description]': name,
        #     'groups[0][name]': name,
        #     'groups[0][courseid]': course_id,
        # }

        # :param name: str  nombre del nuevo grupo
        # :param course_id: int id del curso 
        # :return: dict retorna un diccionario con los valores
        
        params = {
            'groups[0][description]': name,
            'groups[0][name]': name,
            'groups[0][courseid]': course_id,
        }
        function = "core_group_create_groups"
        return self.connect(function, params)

    def get_category_by_field(self, key: str, value: str) -> dict:
        
        # Obtiene la categoria en base al campo y valor 
        # core_course_get_categories

        # :param key: str campo a buscar en la tabla
        # :param value: str valor del campo
        # :return: dict return los resultados
        
        function = "core_course_get_categories"
        params = {
            'criteria[0][key]': key,
            'criteria[0][value]': value
        }
        return self.connect(function, params)

    def update_user_password(self, user_id: int, password: str) -> dict:
        
        # Funcion para actulizar la contraseña de un usuario en moodle

        # Function: core_user_update_users

        # params = {'users[0][id]': user_id   ,'users[0][password]': password}
        # :param user_id: int id del usuario
        # :param password: str nueva contraseña
        # :return: dict 
        
        function = "core_user_update_users"
        params = {'users[0][id]': user_id, 'users[0][password]': password}
        return self.connect(function, params)

    def delete_users(self, user_id: int) -> dict:
        
        # Funcion para borrar un usuario en moodle

        # Function: core_user_delete_users

        # params = {'userids[0]': user_id}
        # :param user_id: int id del usuario
        # :return: dict
        
        function = "core_user_delete_users"
        params = {'userids[0]': user_id}
        return self.connect(function, params)

    def enrol_user(self, course_id: str, user_id: int) -> dict:
        
        # Funcion para la matriculacion en moodle

        # enrol_manual_enrol_users

        # params = {
        #     'enrolments[0][courseid]': course_id,
        #     'enrolments[0][userid]': user_id,
        #     'enrolments[0][roleid]': 5
        # }
        # :param course_id: str id del curso
        # :param user_id: int id del usuario
        # :param roleid: int id del role del usuario por defecto 5 que es estudiante
        # :return: dict
        
        function = "enrol_manual_enrol_users"
        params = {
            'enrolments[0][courseid]': course_id,
            'enrolments[0][userid]': user_id,
            'enrolments[0][roleid]': 5
        }
        return self.connect(function, params)

    def unenrol_user(self, course_id: str, user_id: int) -> dict:
        
        # Funcion para desmatricular en moodle

        # enrol_manual_unenrol_users

        # params = {
        #     'enrolments[0][courseid]': course_id,
        #     'enrolments[0][userid]': user_id,
        #     'enrolments[0][roleid]': 5
        # }
        # :param course_id: str id del curso
        # :param user_id: int id del usuario
        # :param roleid: int id del role del usuario por defecto 5 que es estudiante
        # :return: dict
        
        function = "enrol_manual_unenrol_users"
        params = {
            'enrolments[0][courseid]': course_id,
            'enrolments[0][userid]': user_id,
            'enrolments[0][roleid]': 5
        }
        return self.connect(function, params)

    def get_users_courses(self, user_id: int) -> dict:
        
        # Funcion para extraer todos los cursos en la que se encuentra inscrito un usuario

        # core_enrol_get_users_courses

        # params = {
        #     'userid': user_id
        # }

        # :param user_id: int id del usuario
        # :return: dict diccionario con el resultado 
        
        function = "core_enrol_get_users_courses"
        params = {
            'userid': user_id
        }
        return self.connect(function, params)

    def add_group_members(self, group_id: int, user_id: int) -> dict:
        
        # Funcion para matricular al usuario a un grupo 

        # core_group_add_group_members

        # params = {
        #     'members[0][groupid]': group_id,
        #     'members[0][userid]': user_id
        # }

        # :param group_id: int id del grupo
        # :param user_id: int id del usuario
        # :return: dict
        
        function = "core_group_add_group_members"
        params = {
            'members[0][groupid]': group_id,
            'members[0][userid]': user_id
        }
        return self.connect(function, params)

    def delete_group_member(self, group_id: int, user_id: int) -> dict:
        
        # Funcion para desmatricular al usuario de un grupo 

        # core_group_update_group_members
        # params = {
        #     'members[0][groupid]': group_id, #new group id to update
        #     'members[0][userid]': user_id # user id to update
        # }

        # :param group_id: int id del grupo 
        # :param user_id: int id del usuario
        # :return: dict
        
        function = "core_group_delete_group_members"
        params = {
            'members[0][groupid]': group_id,
            'members[0][userid]': user_id
        }
        return self.connect(function, params)

    def get_group_members(self, group_id: int, user_id: int) -> dict:
        
        # Funcion para obtener los grupos al que pertenece un usuario 

        # core_group_get_group_members

        # params = {
        #     'members[0][groupid]': group_id, #group id to find
        #     'members[0][userid]': user_id # user id to find
        # }

        # :param group_id: int id del grupo
        # :param user_id: int id del usuario
        # :return: dict
        
        function = "core_group_get_group_members"
        params = {
            'members[0][groupid]': group_id,
            'members[0][userid]': user_id
        }
        return self.connect(function, params)

    def get_cohort(self, name: str) -> dict:
        
        # Funcion para obtener las cohortes

        # core_cohort_search_cohorts: Search for cohorts.

        # :param name: str to search nombre de la cohorte 
        # :return: dict of 1 cohort
        
        function = "core_cohort_search_cohorts"
        params = {'query': name,
                  'context[contextid]': 0,
                  'context[contextlevel]': 'system',
                  'context[instanceid]': 0,
                  'limitnum': 1}
        cohorts = self.connect(function, params)
        cohort = None
        if cohorts is not None and cohorts.get('cohorts'):
            cohort = cohorts["cohorts"][0]
        return cohort

    def core_cohort_create_cohorts(self, name):
        
        # Funcion para crear una cohorte 

        # :params name: str nombre de la cohorte 
        # :return dict:

        
        function = "core_cohort_create_cohorts"
        params = {
            'cohorts[0][categorytype][type]': 'system',
            'cohorts[0][categorytype][value]': '',
            'cohorts[0][name]': name,
            'cohorts[0][idnumber]': name,
        }
        return self.connect(function, params)

    def core_cohort_add_cohorts_members(self, cohortid, userid):
        
        # Funcion para agregar o matricular un estudiante a una cohorte

        # :param cohortid: id de la cohorte
        # :param userid: id del usuario 
        # :return dict
        
        function = "core_cohort_add_cohort_members"
        params = {
            'members[0][cohorttype][type]': 'id',
            'members[0][cohorttype][value]': cohortid,
            'members[0][usertype][type]': 'id',
            'members[0][usertype][value]': userid
        }
        return self.connect(function, params)

    def cohort_delete_cohort_members(self, cohort_id, user_id):
    
        # Funcion para eliminar miembros de una cohorte

        # :param cohortid: int id de la cohorte
        # :param user_id: int id del usuario 
        # :return dict:
        
        function = "core_cohort_delete_cohort_members"
        params = {
            'members[0][cohortid]': cohort_id,
            'members[0][userid]': user_id
        }
        return self.connect(function, params)
    
    def get_categories(self):
        function = "core_course_get_categories"
        params = {
            'criteria[0][key]' : '',
            'criteria[0][value]': '',
        }
        return self.connect(function, params)

    def suspend_user_account(self, user_id: int, suspended: bool) -> dict:
        
        # Funcion para activar o desactivar un usuario en moodle

        # Function: core_user_update_users

        # params = {'users[0][id]': user_id   ,'users[0][suspended]': suspended}
        # :param user_id: int id del usuario 
        # :param suspended: bool parametro para activar o desactivar el usuario
        # :return: dict
        
        function = "core_user_update_users"
        params = {'users[0][id]': user_id, 'users[0][suspended]': suspended}
        return self.connect(function, params)
