# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime

import logging
logger = logging.getLogger(__name__)


class MoodleCourses(models.TransientModel):
    _name = 'moodle.courses'

    def action_inactive(self):
        return True

    def action_active(self):
        return True

    @api.model
    def default_get(self,vals):
        res=super(MoodleCourses,self).default_get(vals)
        student_id=self.env['op.student'].browse(self.env.context.get('active_id'))
        moodle_id=student_id.company_id.get_credential()
        if not student_id.email:
            raise UserError( str("El estudiente no tiene definido una Correo electronico"))
        user_moodle = moodle_id.get_user_by_field(field="email",
                                               value=student_id.email)
        active='0'
        if user_moodle.get('suspended')==False:
            active='1'
        if user_moodle is not None:
            user_moodle_id=user_moodle.get('id')
        else:
            raise UserError(str("El estudiente No existe en Moodle"))
        courses=[]
        response =moodle_id.moodle_function(function='core_enrol_get_users_courses', params={
            'userid': user_moodle_id})
        for line in response:
            courses.append((0,0,{
                'number':line['idnumber'],
                'fullname':line['fullname'],
                'category':line['category'],
                'progress':line['progress']
                }))
        res.update({'student_id':student_id.id,'course_ids':courses,'state':active})
        return res

    student_id=fields.Many2one("op.student",string="Estudiante")
    state=fields.Selection([('1','Activo'),('0','Inactivo')],string="Estatus")
    course_ids=fields.One2many("moodle.courses.line","course_id","Course ids")


class MoodleCoursesLine(models.TransientModel):
    _name = 'moodle.courses.line'

    course_id=fields.Many2one("moodle.courses",string="Course ID")
    number=fields.Char(string="idnumber")
    category=fields.Char(string="category")
    fullname=fields.Char(string="Descripcion")
    progress=fields.Float(string="Progreso %")