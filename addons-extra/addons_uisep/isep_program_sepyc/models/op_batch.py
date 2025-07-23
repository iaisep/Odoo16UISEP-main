# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OpBatch(models.Model):
    _inherit = 'op.batch'

    
    @api.onchange('sepyc_program')
    def _onchange_sepyc_program(self):
        self.ensure_one()
        courses = self.env['op.student.course'].search([('batch_id.code', '=', self.code)])
        for course in courses:
            students = self.env['op.student'].search([('id', '=', course.student_id.id)])

            for student in students:
                if self.sepyc_program:
                    student.sepyc_program = True
                else:
                    student.sepyc_program = False
