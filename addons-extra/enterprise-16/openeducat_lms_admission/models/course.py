# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpCourse(models.Model):
    _inherit = "op.course"

    is_enroll_user = fields.Boolean('Enroll User')
    online_course_created = fields.Boolean('Online Course Created')

    def create_online_course(self):
        for rec in self:
            course = self.env['op.course'].search([('id', '=', rec.id)])
            course.write({'online_course': True, 'online_course_created': True})
