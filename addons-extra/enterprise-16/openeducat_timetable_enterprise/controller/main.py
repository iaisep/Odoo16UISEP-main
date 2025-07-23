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
from pytz import timezone

from odoo import _, http
from odoo.http import request
from odoo.osv import expression
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

PPG = 10  # record per page


class TimeTablePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):

        values = super(TimeTablePortal, self)._prepare_portal_layout_values()
        user = request.env.user
        student_id = request.env["op.student"].sudo().search(
            [('user_id', '=', user.id)])
        timetable_count = 0
        for course_id in student_id.course_detail_ids:
            session_count = request.env['op.session'].sudo().search_count(
                [('course_id', '=', course_id.course_id.id)])
            timetable_count += session_count
        values['timetable_count'] = timetable_count
        return values

    def get_search_domain_timetable(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', '|', '|', '|', ('subject_id', 'ilike', srch),
                    ('faculty_id', 'ilike', srch), ('course_id', 'ilike', srch),
                    ('classroom_id', 'ilike', srch), ('state', 'ilike', srch),
                    ('end_datetime', 'ilike', srch), ('start_datetime', 'ilike', srch)
                ]
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

    def _parent_prepare_portal_layout_values(self, student_id=None):

        val = super(TimeTablePortal, self). \
            _parent_prepare_portal_layout_values(student_id)
        student = request.env["op.student"].sudo().search(
            [('id', '=', student_id)])
        timetable_count = 0
        for course_id in student.course_detail_ids:
            session_count = request.env['op.session'].sudo().search_count(
                [('course_id', '=', course_id.course_id.id)])
            timetable_count += session_count
        val['timetable_count'] = timetable_count
        return val

    @http.route(['/student/timetable/',
                 '/student/timetable/<int:student_id>',
                 '/student/timetable/page/<int:page>',
                 '/student/timetable/<int:student_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_student_timetable_list(
            self, student_id=None, date_begin=None, date_end=None, page=0,
            search='', ppg=False, sortby=None, filterby=None,
            search_in='subject_id', groupby='course_id', **post):

        if student_id:
            val = self._parent_prepare_portal_layout_values(student_id)
        else:
            values = self._prepare_portal_layout_values()

        user = request.env.user
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        searchbar_sortings = {
            'name': {'label': _('Meeting Subject'), 'order': 'name'},
            'start_datetime': {'label': _('Start Date'),
                               'order': 'start_datetime'},
            'end_datetime': {'label': _('End Date'), 'order': 'end_datetime'},
            'course_id': {'label': _('Course'), 'order': 'course_id'},
            'subject_id': {'label': _('Subject'), 'order': 'subject_id'},
            'state': {'label': _('State'), 'order': 'state'},
        }

        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        now = datetime.now()
        today = now.strftime("%A")

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'),
                      'domain': [('type', '=', today)]},
            'state draft': {'label': _('Draft'),
                            'domain': [('state', '=', 'draft')]},
            'state confirm': {'label': _('Confirm'),
                              'domain': [('state', '=', 'confirm')]},
            'state done': {'label': _('Done'),
                           'domain': [('state', '=', 'done')]},
            'state cancel': {'label': _('Canceled'),
                             'domain': [('state', '=', 'Cancel')]},
        }

        searchbar_inputs = {
            'subject_id': {'input': 'subject_id',
                           'label': Markup(_('Search<span class="nolabel"> '
                                             '(in subject)</span>'))},
            'faculty': {'input': 'Faculty',
                        'label': _('Search in Faculty')},
            'course': {'input': 'Course',
                       'label': _('Search in Course')},
            'classroom': {'input': 'classroom',
                          'label': _('Search in Classroom')},
            'state': {'input': 'State',
                      'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'course_id': {'input': 'course_id', 'label': _('Course')},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        domain += self.get_search_domain_timetable(search, attrib_values)

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        if student_id:
            keep = QueryURL('/student/timetable/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))

            student = request.env["op.student"].sudo().search(
                [('id', '=', student_id)])

            total = 0
            course_id = [i.course_id.id for i in student.course_detail_ids],
            domain += [('course_id', 'in', course_id[0])]

            session_count = request.env['op.session'].sudo().search_count(
                domain)
            total += session_count

            pager = portal_pager(
                url="/student/timetable/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/student/timetable/', search=search, attrib=attrib_list,
                            order=post.get('order'))

            student = request.env["op.student"].sudo().search(
                [('user_id', '=', user.id)])

            total = 0
            course_id = [i.course_id.id for i in student.course_detail_ids],
            domain += [('course_id', 'in', course_id[0])]

            session_count = request.env['op.session'].sudo().search_count(
                domain)
            total += session_count

            pager = portal_pager(
                url="/student/timetable/",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'subject_id'):
                search_domain = expression.OR(
                    [search_domain, [('subject_id', 'ilike', search)]])
            if search_in in ('all', 'faculty'):
                search_domain = expression.OR(
                    [search_domain, [('faculty_id', 'ilike', search)]])
            if search_in in ('all', 'course'):
                search_domain = expression.OR(
                    [search_domain, [('course_id', 'ilike', search)]])
            if search_in in ('all', 'classroom'):
                search_domain = expression.OR(
                    [search_domain, [('classroom_id', 'ilike', search)]])
            if search_in in ('all', 'state'):
                search_domain = expression.OR(
                    [search_domain, [('state', 'ilike', search)]])
            domain += search_domain

        if groupby == 'course_id':
            order = "course_id, %s" % order

        timetable_lst = []
        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')
            timetable_id = request.env['op.session'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
        else:

            timetable_id = request.env['op.session'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        if timetable_id:
            for rec in timetable_id:
                timetable_lst.append(rec)

        if groupby == 'course_id':
            grouped_tasks = [
                request.env['op.session'].sudo().concat(*g)
                for k, g in groupbyelem(timetable_id, itemgetter('course_id'))]
        else:
            grouped_tasks = [timetable_id]

        if student_id:
            val.update({
                'date': date_begin,
                'timetable_ids': timetable_lst,
                'page_name': 'Timetable_list',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/student/timetable/%s' % student_id,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'grouped_tasks': grouped_tasks,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,

            })
            return request.render(
                "openeducat_timetable_enterprise.openeducat_timetable_portal",
                val)
        else:
            values.update({
                'date': date_begin,
                'timetable_ids': timetable_lst,
                'page_name': 'Timetable_list',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/student/timetable/',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'grouped_tasks': grouped_tasks,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,
            })

            return request.render(
                "openeducat_timetable_enterprise.openeducat_timetable_portal",
                values)

    @http.route('/get-timetable/data', type='json', auth='user', website=True)
    def get_timetable_data_portal(self, stud_id=None, current_timezone=None):
        data = []
        course_list = []
        batch_list = []
        all_lession = ''
        if stud_id:

            student = request.env['op.student'].sudo().search(
                [('id', '=', int(stud_id))])
        else:
            student = request.env['op.student'].sudo().search(
                [('user_id', '=', request.env.uid)])

        for course in student.course_detail_ids:
            course_list.append(course.course_id.id)
            batch_list.append(course.batch_id.id)

        session_model = request.env['op.session'].sudo().search(
            [('course_id', 'in', course_list),
             ('batch_id', 'in', batch_list)])
        user_tz = request.env.user.tz or current_timezone or 'UTC'
        for session in session_model:
            for lesson in session.lesson_ids:
                all_lession += lesson.lesson_topic
            data.append({
                'title': session.subject_id.name,
                'start': session.start_datetime.astimezone(timezone(user_tz)),
                'end': session.end_datetime.astimezone(timezone(user_tz)),
                'faculty': session.faculty_id.name,
                'batch': session.batch_id.name,
                'course': session.course_id.name,
                'day': session.type,
                'time': session.timing,
                'lesson': all_lession
            })
        return data
