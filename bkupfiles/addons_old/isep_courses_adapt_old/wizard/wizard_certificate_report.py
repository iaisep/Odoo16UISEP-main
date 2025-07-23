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


class IsepCertifiesReport(models.TransientModel):
    _name= "isep.certifies.report"

    @api.model
    def default_get(self,vals):
        res=super(IsepCertifiesReport,self).default_get(vals)
        student_obj = self.env.context.get('active_id', []) or []
        student_id = self.env['op.student'].search([('id', '=', student_obj)])
        admission_ids = self.env['op.admission'].search([('student_id', '=', student_id.id)])
        res.update({'student_id':student_id.id})
        return res

    def _set_certified(self):
        return [('model', 'like', '%op.student%')]

    def _set_courses(self):
        student_id = self.env.context.get('active_id', []) or []
        admission_ids = self.env['op.admission'].search([('student_id', '=', student_id.id)])
        courses = []
        for course in admission_ids:
            courses.append(course.batch_id.id)
        return [('id', 'in', courses)]


    student_id = fields.Many2one('op.student', string="Estudiente",required=True)
    course_id = fields.Many2one('op.course', string="Curso")
    file_id = fields.Many2one('ir.actions.report', string="Archivo",
                              domain=_set_certified, required=True)
    batch_id = fields.Many2one('op.batch', string="Grupo", required=True)
    batch_ids = fields.Many2many('op.batch', string="Grupos")


    def verify_debt(self):
        return True
        #if 'Diploma' in self.file_id.name and self.student_id.delay:
        #    raise UserError('Este estudiante esta bloqueado por morosidad!!!')

    def print_diploma_certify(self):
        self.verify_debt()
        return self.env['ir.actions.report'].sudo().search([('id','=',self.file_id.id)]).report_action(self)