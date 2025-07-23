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
import string
import random
LETTERS = string.ascii_letters
NUMBERS = string.digits
PUNCTUATION = '@@$#*-'


class OpAdmission(models.Model):
    _inherit = "op.admission"

    def wizard_enroll_student(self):
        self.ensure_one()
        module=__name__.split('addons.')[1].split('.')[0]
        view=self.env.ref('%s.view_moodle_admission_wizard_from'%module)
        #if not self.course_id.moodle_category_ids:
        #    raise ValidationError(_("No se econtro categoría en Moodle "))
            
        return {
            'name':'MATRICULAR ESTUDIENTE',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'moodle.admission.wizard',
            'view_id':view.id,
            'target':'new',
            'type':'ir.actions.act_window'
        }

    @staticmethod
    def password_generator(length=18):
        printable = f'{PUNCTUATION}{LETTERS}{NUMBERS}{PUNCTUATION}' + '1'
        printable = list(printable)
        random.shuffle(printable)
        random_password = random.choices(printable, k=length)
        random_password = ''.join(random_password)
        return random_password

    def enroll_student_moodle(self,moodle_courses_ids):
        self.enroll_student()

        student_course = self.env['op.student.course'].search(
            [('student_id', '=', self.student_id.id),
             ('batch_id', '=', self.batch_id.id)])

        student_values = {}
        send_password = False
        if self.student_id:
            gr_no='0'
            if not self.student_id.gr_no:
                gr_no = self.env['ir.sequence'].next_by_code('op.gr.number')
            moodle = self.company_id.get_credential()
            moodle_groups = []
            for moodle_course_id in moodle_courses_ids:
                moodle_group = moodle.get_group(moodle_course_id,
                                                self.batch_id.code)
                if moodle_group is None:
                    moodle_group = moodle.core_group_create_groups(
                        self.batch_id.code, moodle_course_id)
                moodle_groups.append(moodle_group)

            password = self.password_generator(length=18)
            user = moodle.get_user_by_field(field="email",
                                        value=self.student_id.email.lower().strip())
            if user is None:
                first_name = self.first_name
                if self.middle_name:
                    first_name = ' '.join([first_name, self.middle_name])

                user_response = moodle.create_users(
                    firstname=first_name,
                    lastname=self.last_name,
                    dni=self.partner_id.vat,
                    password=password,
                    email=self.partner_id.email.lower().strip())
                user = user_response[0]
                student_values.update({
                    'moodle_id': user.get('id'),
                    'moodle_user': self.student_id.email,
                    'moodle_pass': password,
                    'gr_no': gr_no,
                })
                self.student_id.write(student_values)
                send_password = True
            if not self.student_id.moodle_id:
                student_values.update({
                    'moodle_id': user.get('id'),
                    'moodle_user': user.get('username')
                })
                self.student_id.write(student_values)
            student_course.write({'roll_number': gr_no})
            for moodle_course_id in moodle_courses_ids:
                """Se inscribe al estudiante en los diferentes cursos que fueron seleccionados"""
                enrol_result = moodle.enrol_user(moodle_course_id,
                                             user.get('id'))
            for moodle_group in moodle_groups:
                """Se agrega al estudiante en los diferentes grupos"""
                if type(moodle_group) == dict:
                    member_result = moodle.add_group_members(
                        moodle_group.get('id'), user.get('id'))
                else:
                    member_result = moodle.add_group_members(
                        moodle_group[0].get('id'), user.get('id'))

            if 'ATH' in self.batch_id.code or 'PRS' in self.batch_id.code:
                """
                Se verifica si el curso es ATHOME o PRESENCIAL
                para crear la cohorte

                Actualmente no usado
                """
                moodle_cohort = moodle.get_cohort(self.batch_id.code)
                if moodle_cohort is None:
                    moodle_cohort = moodle.core_cohort_create_cohorts(
                        self.batch_id.code)
                if type(moodle_cohort) == dict:
                    cohort_member = moodle.core_cohort_add_cohorts_members(
                        moodle_cohort.get('id'), user.get('id'))
                else:
                    cohort_member = moodle.core_cohort_add_cohorts_members(
                        moodle_cohort[0].get('id'), user.get('id'))
            if send_password:
                self.student_id.action_send_access_moodle()
        return True

