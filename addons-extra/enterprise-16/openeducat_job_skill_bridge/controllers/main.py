# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class StudentSkillPortal(CustomerPortal):

    @http.route(['/student/skill',
                 '/student/skill/page/<int:page>'],
                type='http', auth="user", website=True)
    def enterprise_portal_student_skill(self, **kw):

        partner_id = request.env.user.partner_id
        student_id = request.env['op.student'].sudo().search(
            [('partner_id', '=', partner_id.id)])
        skill_id = request.env['op.student.skill.name'].sudo().search([(
            'self_assessed', '=', True)])
        level_id = request.env['op.student.skill.level.name'].sudo().search([])

        return request.render(
            "openeducat_job_skill_bridge.enterprise_add_student_skill_portal",
            {'skill_ids': skill_id,
             'level_id': level_id,
             'user': student_id,
             'page_name': 'student_skill_form'
             })

    @http.route(['/student/skill/submit',
                 '/student/skill/submit/page/<int:page>'],
                type='http', auth="user", website=True)
    def enterprise_portal_add_student_skill(self, **kw):
        vals = {
            'student_id': kw['student_id'],
            'skill_type_id': kw['skill_type_id'],
            'level_id': kw['level_id']
        }
        partner_id = request.env.user.partner_id
        student_id = request.env['op.student'].sudo().search(
            [('partner_id', '=', partner_id.id)])

        student_id.skill_line.sudo().create(vals)

        return request.redirect('/student/profile')
