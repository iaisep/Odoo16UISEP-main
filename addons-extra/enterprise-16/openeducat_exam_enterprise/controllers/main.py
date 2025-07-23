# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from collections import OrderedDict
from operator import itemgetter

from markupsafe import Markup

from odoo import _, http
from odoo.http import Response, request
from odoo.osv import expression
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL


class Exam(http.Controller):

    @http.route("/get_exam_counts", type="json", auth="user")
    def get_exams(self):
        Exam = request.env['op.exam']
        all_exams = Exam.search_count([])
        done_exams = Exam.search_count([('state', '=', 'done')])
        pending_exams = Exam.search_count([('state', '=', 'draft')])
        all_exams_sessions = request.env['op.exam.session'].search_count([])

        return {
            'all_exams': all_exams,
            'pending_exams': pending_exams,
            'done_exams': done_exams,
            'all_exams_sessions': all_exams_sessions
        }

    def get_details(self, domain, subject=False):
        data = []
        for exam in request.env['op.exam'].search(domain):
            pass_count = 0
            res = {}
            for attendant in exam.attendees_line.filtered( # noqa
                    lambda att: att.marks >= exam.min_marks):
                pass_count += 1
            lengths = len(exam.attendees_line) if exam.attendees_line else 1
            ratio = (pass_count / lengths) * 100
            if subject:
                res = {
                    'id': exam.id,
                    'name': exam.subject_id.name,
                    'exam': exam.name,
                    'code': exam.exam_code,
                    'start_time': exam.start_time or False,
                    'end_time': exam.end_time or False,
                    'min_marks': exam.min_marks or 0.0,
                    'total_marks': exam.total_marks or 0.0,
                }
            else:
                res = {
                    'name': exam.name,
                    'ratio': ratio
                }
            data.append(res)
        return data

    @http.route("/get_exam_chart_details", type="json", auth="user")
    def get_exam_chart_details(self):
        return self.get_details([('attendees_line', '!=', False)])

    @http.route("/get_subject_details", type="json", auth="user")
    def get_subject_details(self, session_id):
        return self.get_details([
            ('session_id', '=', int(session_id))], subject=True)

    @http.route("/get_exam_sessions", type="json", auth="user")
    def get_exam_sessions(self):
        return {
            'session_ids': request.env['op.exam.session'].search_read(
                [], ['id', 'name'])
        }


PPG = 10  # record per page


class ExamPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):

        values = super(ExamPortal, self)._prepare_portal_layout_values()
        user = request.env.user
        student_id = request.env["op.student"].sudo().search(
            [('user_id', '=', user.id)])
        exam_count = request.env['op.marksheet.line'].sudo().search_count(
            [('student_id', '=', student_id.id)])
        values['exam_count'] = exam_count
        return values

    def _parent_prepare_portal_layout_values(self, student_id=None):

        val = super(ExamPortal, self). \
            _parent_prepare_portal_layout_values(student_id)

        exam_count = request.env['op.marksheet.line'].sudo().search_count(
            [('student_id', '=', student_id)])
        val['exam_count'] = exam_count
        return val

    def get_search_domain_exam(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', ('total_marks', 'ilike', srch),
                    ('percentage', 'ilike', srch), ('status', 'ilike', srch)
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

    @http.route(['/student/exam/',
                 '/student/exam/<int:student_id>',
                 '/student/exam/page/<int:page>',
                 '/student/exam/<int:student_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_student_exam_list(self, student_id=None, date_begin=None, date_end=None,
                                 page=0, search='', search_in='total_marks', ppg=False,
                                 sortby=None, filterby=None, groupby='none', **post):
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
            'percentage': {'label': _('percentage(%)'),
                           'order': 'percentage desc'},
            'grade': {'label': _('Grade'), 'order': 'grade'},
            'generated_date': {'label': _('Generated Date'),
                               'order': 'generated_date desc'},
            'status': {'label': _('Status'), 'order': 'status'},
            'total_marks': {'label': _('Total Marks'),
                            'order': 'total_marks desc'}
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'pass': {'label': _('Pass'), 'domain': [('status', '=', 'pass')]},
            'fail': {'label': _('Fail'), 'domain': [('status', '=', 'fail')]},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if not sortby:
            sortby = 'generated_date'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        searchbar_inputs = {
            'total_marks': {'input': 'total_marks',
                            'label': Markup(_('Search <span class="nolabel">'
                                              '(in Total Marks)</span>'))},
            'percentage': {'input': 'Course',
                           'label': _('Search in Percentage')},
            'status': {'input': 'Status',
                       'label': _('Search in Status')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'status': {'input': 'status', 'label': _('Status')},
        }

        domain += self.get_search_domain_exam(search, attrib_values)

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'total_marks'):
                search_domain = expression.OR(
                    [search_domain, [('total_marks', 'ilike', search)]])
            if search_in in ('all', 'percentage'):
                search_domain = expression.OR(
                    [search_domain, [('percentage', 'ilike', search)]])
            if search_in in ('all', 'status'):
                search_domain = expression.OR(
                    [search_domain, [('status', 'ilike', search)]])
            domain += search_domain

        if student_id:
            keep = QueryURL('/student/exam/%s' % student_id,
                            search=search, amenity=attrib_list,
                            order=post.get('order'))
            domain += [('student_id', '=', student_id)]
            total = request.env['op.marksheet.line'].sudo().search_count(domain)
            pager = portal_pager(
                url="/student/exam/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in, },
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/student/exam/', search=search,
                            amenity=attrib_list, order=post.get('order'))
            student = request.env["op.student"].sudo().search(
                [('user_id', '=', user.id)])
            domain += [('student_id', '=', student.id)]
            total = request.env['op.marksheet.line'].sudo().search_count(domain)

            pager = portal_pager(
                url="/student/exam/",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in, },
                total=total,
                page=page,
                step=ppg
            )

        if groupby == 'None':
            order = "status %s" % order

        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')
            exam_id = request.env['op.marksheet.line'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
        else:
            exam_id = request.env['op.marksheet.line'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        if groupby == 'None':
            grouped_tasks = [
                request.env['op.marksheet.line'].sudo().concat(*g)
                for k, g in groupbyelem(exam_id, itemgetter('None'))]
        else:
            grouped_tasks = [exam_id]

        if student_id:
            val.update({
                'date': date_begin,
                'exam_ids': exam_id,
                'page_name': 'Exam_List',
                'pager': pager,
                'ppg': ppg,
                'stud_id': student_id,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/student/exam/%s' % student_id,
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
                "openeducat_exam_enterprise.openeducat_exam_portal",
                val)
        else:
            values.update({
                'date': date_begin,
                'exam_ids': exam_id,
                'page_name': 'Exam_List',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/student/exam/',
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
                "openeducat_exam_enterprise.openeducat_exam_portal",
                values)

    def check_exam_access(self, exam_id=None):

        marksheet_id = request.env['op.marksheet.line'].sudo().search(
            [('id', '=', exam_id)])
        user = request.env.user
        user_list = []
        count = 0
        for rec in marksheet_id.student_id:
            if rec.user_id:
                user_list.append(rec.user_id)

        if user.partner_id.is_parent:
            parent_id = request.env['op.parent'].sudo().search(
                [('name', '=', user.partner_id.id)])
            for student_id in parent_id.student_ids:
                if student_id.user_id in user_list:
                    count += 1
            if count > 0:
                return True
            else:
                return False
        else:
            if user not in user_list:
                return False
            else:
                return True

    @http.route(['/student/exam/data/<int:exam_id>',
                 '/student/exam/data/<int:student_id>/<int:exam_id>', ],
                type='http', auth="user", website=True)
    def portal_student_exam_form(self, student_id=None, exam_id=None, ):

        exam_instance = request.env['op.marksheet.line'].sudo().search(
            [('id', '=', exam_id)])
        access_role = self.check_exam_access(exam_instance.id)
        if access_role is False:
            return Response("[Bad Request]", status=404)

        return request.render(
            "openeducat_exam_enterprise.openeducat_exam_portal_data",
            {'exam_id': exam_instance,
             'student': student_id,
             'page_name': 'exam_merksheet_info'})
