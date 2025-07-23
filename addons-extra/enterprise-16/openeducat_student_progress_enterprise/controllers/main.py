# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class StudentProgression(CustomerPortal):

    @http.route(['/student/progression/',
                 '/student/progression/<int:student_id>',
                 '/student/progression/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_student_progression(self, student_id=None):

        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')
            progression_id = request.env['op.student.progression']. \
                sudo().search([('student_id', '=', student_id)])
        else:
            user = request.env.user
            student_id = request.env['op.student'].sudo(). \
                search([('user_id', '=', user.id)])
            progression_id = \
                request.env['op.student.progression'].sudo().search(
                    [('student_id', '=', student_id.id)])

        return request.render(
            "openeducat_student_progress_enterprise."
            "openeducat_student_progression_portal_data",
            {'progression': progression_id,
             'stud_id': student_id,
             'page_name': 'student_progress_info', })
