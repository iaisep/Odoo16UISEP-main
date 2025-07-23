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


import logging
logger = logging.getLogger(__name__)

class OpStudent(models.Model):
    _inherit = "op.student"

    exam_attendees_count = fields.Integer(
        compute='_compute_exam_attendees_count', default=0)
    exam_attendees_ids = fields.One2many("op.exam.attendees", "student_id",
                                         string="Exam attendees")
    sale_count = fields.Integer(string="Ventas", default=0)
    moodle_id = fields.Integer(string='Moodle ID')
    moodle_user = fields.Char(string='Moodle user', size=128)
    moodle_pass = fields.Char(string='Moodle Password', size=24)

    def action_view_sale(self):
        return True

    def action_wizard_certificate(self):
        self.ensure_one()
        module=__name__.split('addons.')[1].split('.')[0]
        view=self.env.ref('%s.view_isep_certifies_report_from'%module)
        return {
            'name':'DIPLOMAS  Y CERTIFICADOS',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'isep.certifies.report',
            'view_id':view.id,
            'target':'new',
            'type':'ir.actions.act_window'
        }

    def action_status_moodle(self):
        self.ensure_one()
        module=__name__.split('addons.')[1].split('.')[0]
        view=self.env.ref('%s.view_moodle_courses_from'%module)
        return {
            'name':'Moodle View',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'moodle.courses',
            'view_id':view.id,
            'target':'new',
            'type':'ir.actions.act_window'
        }

    def _compute_exam_attendees_count(self):
        for student in self:
            student.exam_attendees_count = len(student.exam_attendees_ids)

    def action_open_exam_attendees(self):
        self.ensure_one()
        exam_attendees = self.exam_attendees_ids
        action = self.env.ref(
            'openeducat_exam.act_open_op_exam_attendees_view').read()[0]
        if len(exam_attendees) > 1:
            action['domain'] = [('id', 'in', exam_attendees.ids)]
            action['context'] = "{'group_by': 'course_id'}"
        elif len(exam_attendees) == 1:
            form_view = [(self.env.ref(
                'openeducat_exam.view_op_exam_attendees_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in
                                               action['views'] if
                                               view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = exam_attendees.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_generate_grades(self):
        for this in self:
            for admission in this.course_detail_ids:
                batch_id = admission.batch_id
                course_id = admission.course_id
                for subject_rel in admission.subject_ids: 
                    exam_session = self.env['op.exam.session'].search([
                            ('course_id', '=', course_id.id),
                            ('batch_id', '=', batch_id.id)
                        ], limit=1)
                    if not exam_session:
                        exam_session = self.env['op.exam.session'].search([('exam_code', '=', batch_id.code)], limit=1)
                        exam_type=self.env['']
                        if not exam_session:
                            exam_type = self.env['op.exam.type'].search([('code','=','SUBJ')], limit=1)
                            if not exam_type:
                                exam_type=self.env['op.exam.type'].create({'name':'Asignatura','code':'SUBJ'})

                            ##
                            venue=self.env['res.partner'].search([('name','=','ISEP')], limit=1)
                            if not venue:
                                venue=self.env['res.partner'].create({'name':'ISEP'})
                            exam_session = self.env['op.exam.session'].create({
                                'name': batch_id.code,
                                'course_id': course_id.id,
                                'batch_id': batch_id.id,
                                'exam_code': batch_id.code,
                                'start_date': batch_id.start_date,
                                'end_date': batch_id.end_date,
                                'exam_type':exam_type.id,
                                'evaluation_type': 'grade',
                                'venue':venue.id
                            })
                    exam = self.env['op.exam'].search([
                            ('subject_id', '=', subject_rel.id),
                            ('session_id', '=', exam_session.id),
                            ('exam_code', '=',subject_rel.code)
                        ], limit=1)
                    if not exam:
                        val={
                            'subject_id': subject_rel.id,
                            'session_id': exam_session.id,
                            'name': exam_session.name + '-' + subject_rel.code,
                            'exam_code':subject_rel.code,
                            'total_marks': 10,
                            'min_marks': 5,
                            'start_time': exam_session.start_date,
                            'end_time': exam_session.end_date
                        }
                        exam=self.env['op.exam'].create(val)
                    attendee = self.env['op.exam.attendees'].search([
                        ('student_id', '=', this.id),
                        ('exam_id', '=', exam.id)], limit=1)
                    if not attendee:
                        self.env['op.exam.attendees'].create({
                            'exam_id': exam.id,
                            'student_id': this.id,
                            'batch_id': admission.batch_id.id,
                            'course_id': admission.course_id.id,
                            'marks': 0,
                            'status': 'present'
                        })
        return True

    def action_get_grades(self):
        self.action_generate_grades()
        moodle_id=self.company_id.get_credential()
        if not self.email:
            raise UserError( str("El estudiente no tiene definido una Correo electronico"))
        user_moodle = moodle_id.get_user_by_field(field="email",
                                               value=self.email)
        user_moodle_id=False
        if user_moodle is not None:
            user_moodle_id=user_moodle.get('id')
        else:
            raise UserError(str("El estudiente No existe en Moodle"))
        response =moodle_id.moodle_function(function='core_enrol_get_users_courses', params={
            'userid': user_moodle_id})
        for line in response:
            courseid=line.get('id',False)
            if courseid:
                respons_grade=moodle_id.moodle_function(function='gradereport_user_get_grade_items', params={
                    'userid': user_moodle_id,
                    'courseid':courseid})
                #raise UserError( str(respons_grade ))
                if len(respons_grade)>2:
                    raise UserError(str("Revisar mas de 2 items  respons_grade"))

                grade=list(filter(lambda x:x.get('itemtype')=='course' and x.get('graderaw')!=None,respons_grade.get('usergrades')[0].get('gradeitems')  ))
                #raise UserError( str(grade ))
                if not grade:
                    continue
                if len(grade)>1:
                    raise UserError(str("Revisar mas de 2 items  grade"))
                idnumber=respons_grade.get('usergrades')[0].get('courseidnumber')
                graderaw=grade[0].get('graderaw')
                odoocourse=self.exam_attendees_ids.filtered(lambda x:x.exam_id.exam_code==idnumber)
                odoocourse.write({'marks':graderaw})
        return True

    def action_send_access_moodle(self):
        mail_template = self.env.ref('isep_courses_adapt.student_welcome_template_latam')
        mail_template.send_mail(self.id, force_send=True)
        return True

class OpExamAttendees(models.Model):
    _inherit = "op.exam.attendees"

    marks = fields.Float('Marks')