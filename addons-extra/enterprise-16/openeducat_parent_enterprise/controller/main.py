# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class ParentCorePotal(CustomerPortal):

    def _parent_prepare_portal_layout_values(self, student_id=None):
        val = super(
            ParentCorePotal, self)._parent_prepare_portal_layout_values(student_id)
        student = request.env['op.student'].sudo().search([('id', '=', student_id)])

        quiz_module = request.env['ir.model'].sudo().search(
            [('model', '=', 'op.quiz.result')])
        if quiz_module:
            quiz_count = request.env['op.quiz.result'].sudo().search_count(
                [('user_id', '=', student.user_id.id), ('state', '=', 'done')])
            val['quiz_count'] = quiz_count

        course_enroll = request.env['ir.model'].sudo().search(
            [('model', '=', 'op.course.enrollment')])
        if course_enroll:
            course_count = request.env['op.course.enrollment'].sudo().search_count(
                [('user_id', '=', student.user_id.id),
                 ('state', 'in', ['in_progress', 'done'])])
            val['course_count'] = course_count

        digital_library = request.env['ir.model'].sudo().search(
            [('model', '=', 'op.digital.library.enrollment')])
        if digital_library:
            digi_library_count = request.env['op.digital.library.enrollment'].sudo() \
                .search_count([('user_id', '=', student.user_id.id)])
            val['my_library_count'] = digi_library_count

        return val

    @http.route(['/my/child/<int:child_id>'],
                type='http', auth="user", website=True)
    def portal_child_detail(self, child_id=None, **kw):
        values = self._parent_prepare_portal_layout_values(child_id)
        student_id = request.env['op.student'].sudo().search(
            [('id', '=', child_id)])

        access_role = self.check_access_role(student_id)
        if not access_role:
            return request.render("website.404")

        menu_list = request.env['openeducat.portal.menu'].sudo().search(
            [('is_visible_to_parent', '=', True)])

        values.update({'is_parent': True,
                       'student_id': str(student_id.id),
                       'stu_id': student_id,
                       'menu_list': menu_list})

        return request.render("portal.portal_my_home", values)

    @http.route(['/my/child',
                 '/my/child/<int:student_id>',
                 '/my/child/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_child_parent(self, student_id=None, date_begin=None,
                            date_end=None, page=1, search='', ppg=False,
                            sortby=None, filterby=None, **post):
        values = self._parent_prepare_portal_layout_values(student_id)

        user = request.env.user

        total = request.env['op.parent'].sudo().search_count(
            [('user_id', '=', user.id)])

        pager = portal_pager(
            url="/my/child",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby, 'filterby': filterby,
                      'search': search, },
            total=total,
            page=page,
            step=self._items_per_page
        )

        parent = request.env['op.parent'].sudo().search([
            ('user_id', '=', user.id)], limit=self._items_per_page,
            offset=pager['offset'])

        values.update({
            'date': date_begin,
            'child_ids': parent.student_ids,
            'page_name': 'parent_child_List',
            'pager': pager,
            'default_url': '/my/child',

        })
        return request.render(
            "openeducat_parent_enterprise.portal_children_data", values)
