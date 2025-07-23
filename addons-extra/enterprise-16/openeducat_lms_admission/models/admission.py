# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpAdmission(models.Model):
    _name = "op.admission"
    _inherit = "op.admission"

    def enroll_student(self):
        res = super(OpAdmission, self).enroll_student()
        enroll_obj = self.env['op.course.enrollment']
        course = self.env['op.course'].search([
            ('id', '=', self.course_id.id)])
        if course and self.course_id.is_enroll_user is True:
            enroll_obj.create({
                'course_id': self.course_id.id,
                'user_id': self.student_id.user_id.id,
                'enrollment_date': fields.Datetime.now(),
                'state': 'in_progress',
                })
        return res
