# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from collections import OrderedDict
from datetime import datetime
from operator import itemgetter

from markupsafe import Markup

from odoo import _, http
from odoo.http import request
from odoo.osv import expression
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

# from odoo.osv.expression import OR

PPG = 10  # record List per page


class AttendancePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(AttendancePortal, self)._prepare_portal_layout_values()
        user = request.env.user
        student_id = request.env["op.student"].sudo().search(
            [('user_id', '=', user.id)])
        attendance_count = request.env['op.attendance.line'].sudo().search_count(
            [('student_id', '=', student_id.id)])
        values['attendance_count'] = attendance_count
        return values

    def _parent_prepare_portal_layout_values(self, student_id=None):

        val = super(AttendancePortal, self). \
            _parent_prepare_portal_layout_values(student_id)
        attendance_count = request.env['op.attendance.line'].sudo(). \
            search_count([('student_id', '=', student_id)])
        val['attendance_count'] = attendance_count
        return val

    def get_search_domain(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', ('attendance_id', 'ilike', srch),
                    ('batch_id', 'ilike', srch), ('course_id', 'ilike', srch),
                    ('attendance_date', 'ilike', srch)]
        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]
        return domain

    @http.route(['/student/attendance/',
                 '/student/attendance/<int:student_id>',
                 '/student/attendance/page/<int:page>',
                 '/student/attendance/<int:student_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_student_attendance_list(
            self, student_id=None, date_begin=None, date_end=None, page=0,
            search='', search_in='content', ppg=False, sortby=None, filterby=None,
            groupby='course_id', **post):

        if student_id:
            val = self._parent_prepare_portal_layout_values(student_id)
        else:
            values = self._prepare_portal_layout_values()

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        searchbar_sortings = {
            'attendance_id': {'label': _('Attendance Sheet'), 'order': 'attendance_id'},
            'attendance_date': {'label': _('Date'), 'order': 'attendance_date desc'},
            'course_id': {'label': _('Course'), 'order': 'course_id'},
        }
        if not sortby:
            sortby = 'attendance_date'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')

        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [('attendance_date', '=', today)]},
            'present': {'label': _('Present'), 'domain': [('present', '=', True)]},
            'absent': {'label': _('Absent'), 'domain': [('present', '=', False)]},
        }

        searchbar_inputs = {
            'content': {'input': 'content',
                        'label': Markup(_('Search <span class="nolabel"> '
                                          '(in Attendance Sheet)</span>'))},
            'attendance_date': {'input': 'AttendanceDate',
                                'label': _('Search in AttendanceDate')},
            'course': {'input': 'Course', 'label': _('Search in Course')},
            'batch': {'input': 'Batch', 'label': _('Search in Batch')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'course_id': {'input': 'course_id', 'label': _('Course')},
        }

        attendances = request.env['op.attendance.line'].sudo().search([])
        for attendance in attendances:
            searchbar_filters.update({
                str(attendance.course_id.id):
                    {'label': attendance.course_id.name,
                     'domain': [('course_id', '=', attendance.course_id.id)]}
            })

        project_groups = request.env['op.attendance.line'].sudo(). \
            read_group([('id', 'not in', attendances.ids)],
                       ['attendance_id'], ['attendance_id'])

        for group in project_groups:
            proj_id = group['attendance_id'][0] \
                if group['attendance_id'] else False
            proj_name = group['attendance_id'][1] \
                if group['attendance_id'] else _('Others')
            searchbar_groupby.update({
                str(proj_id): {'label': proj_name,
                               'domain': [('attendance_id', '=', proj_id)]}
            })

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'content'):
                search_domain = expression.OR(
                    [search_domain, ['|', ('attendance_id', 'ilike', search),
                                     ('remark', 'ilike', search)]])
            if search_in in ('all', 'attendance_date'):
                search_domain = expression.OR(
                    [search_domain, [('attendance_date', 'ilike', search)]])
            if search_in in ('all', 'course'):
                search_domain = expression.OR(
                    [search_domain, [('course_id', 'ilike', search)]])
            if search_in in ('all', 'batch'):
                search_domain = expression.OR(
                    [search_domain, [('batch_id', 'ilike', search)]])
            domain += search_domain

        student = request.env["op.student"].sudo().search(
            [('user_id', '=', request.env.user.id)])

        domain += self.get_search_domain(search, attrib_values)

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        if student_id:
            keep = QueryURL('/student/attendance/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))
            domain += [('student_id', '=', student_id)]
            total = request.env['op.attendance.line'].sudo().search_count(domain)
            pager = portal_pager(
                url="/student/attendance/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )

        else:
            keep = QueryURL('/student/attendance/',
                            search=search, attrib=attrib_list,
                            order=post.get('order'))
            domain += [('student_id', '=', student.id)]
            total = request.env['op.attendance.line'].sudo().search_count(domain)

            pager = portal_pager(
                url="/student/attendance/",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )

        if groupby == 'course_id':
            order = "course_id, %s" % order

        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')
            attendance_id = request.env['op.attendance.line'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
            attributes = request.env['op.attendance.line'].browse(attendance_id)
        else:
            attendance_id = request.env['op.attendance.line'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
            attributes = request.env['op.attendance.line'].browse(attendance_id)

        if groupby == 'course_id':
            grouped_tasks = [
                request.env['op.attendance.line'].sudo().concat(*g)
                for k, g in groupbyelem(attendance_id, itemgetter('course_id'))]
        else:
            grouped_tasks = [attendance_id]

        if student_id:

            val.update({
                'date': date_begin,
                'attendance_ids': attendance_id,
                'page_name': 'Attendance_Id',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'search': search,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/student/attendance/%s' % student_id,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'grouped_tasks': grouped_tasks,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,
                'attributes': attributes,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,

            })
            return request.render(
                "openeducat_attendance_enterprise.openeducat_attendance_portal",
                val)
        else:

            values.update({
                'date': date_begin,
                'attendance_ids': attendance_id,
                'page_name': 'Attendance_Id',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'search': search,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/student/attendance/',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'grouped_tasks': grouped_tasks,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,
                'attributes': attributes,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,

            })

            return request.render(
                "openeducat_attendance_enterprise.openeducat_attendance_portal",
                values)
