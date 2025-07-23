# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import calendar
from collections import OrderedDict
from datetime import date, datetime
from operator import itemgetter

from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from pytz import timezone as abcd

from odoo import _, fields, http
from odoo.http import Response, request
from odoo.osv import expression
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL


class StudentPortal(CustomerPortal):

    def check_access_role(self, student):
        user = request.env.user.partner_id
        if student.partner_id.id != user.id:
            parent_list = []
            for parent in student.parent_ids:
                parent_list.append(parent.user_id.partner_id.id)
            if user.id in parent_list:
                return True
            else:
                return False
        else:
            return True

    def get_student(self, student_id=None, **kw):

        partner = request.env.user.partner_id
        student_obj = request.env['op.student']
        if not student_id:
            student = student_obj.sudo().search([
                ('partner_id', '=', partner.id)])
        else:
            student = student_obj.sudo().browse(student_id)

            access_role = self.check_access_role(student)
            if not access_role:
                return False

        return student

    @http.route(['/student/profile',
                 '/student/profile/<int:student_id>',
                 '/student/profile/page/<int:page>'],
                type='http', auth="user", website=True)
    def enterprise_portal_student_information(self, student_id=None):

        if student_id:
            student_data = self.get_student(student_id=student_id)
        else:
            student_data = self.get_student()

        if not student_data:
            return request.render('website.404')

        if student_data.partner_id.image_1920:
            student_img = student_data.partner_id.image_1920.decode("utf-8")
        else:
            student_img = student_data.partner_id.image_1920

        return request.render(
            "openeducat_core_enterprise.openeducat_enterprise_student_portal",
            {
                'student': student_data,
                'stud_id': student_id,
                'student_image': student_img,
                'page_name': 'student_profile',
            })

    def get_search_domain_academic_calendar(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', ('name', 'ilike', srch),
                    ('end_date', 'ilike', srch), ('start_date', 'ilike', srch)
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

    @http.route(['/my/academic-calendar/',
                 '/my/academic-calendar/<int:student_id>',
                 '/my/academic-calendar/page/<int:page>',
                 '/my/academic-calendar/<int:student_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_academic_calendar(self, student_id=None, sortby=None,
                                 search='', page=0, ppg=False,
                                 start_date=None, end_date=None,
                                 groupby='start_date', filterby=None,
                                 search_in='all', **post):

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
            'start_date': {'label': _('Start Date'),
                           'order': 'start_date'},
            'end_date': {'label': _('End Date'), 'order': 'end_date'},
        }

        if not sortby:
            sortby = 'start_date'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")]
                         for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        today = datetime.now().date()

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'),
                      'domain': [('start_date', '>', today),
                                 ('end_date', '<', today)]}}

        searchbar_inputs = {
            'name': {'input': 'name',
                     'label': Markup(_('Search<span class="nolabel"> '
                                       '(in name)</span>'))},
            'start_date': {'input': 'Faculty',
                           'label': _('Search in Start Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'start_date': {'input': 'start_date', 'label': _('Start Date')},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        domain += self.get_search_domain_academic_calendar(
            search, attrib_values)

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list
        config_para = request.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'global_calendar_user_id')])
        if student_id:
            keep = QueryURL('/my/academic-calendar/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))

            student_id = request.env["op.student"].sudo().search(
                [('id', '=', student_id)])

            total = 0
            course_list = [
                course.course_id.id for course in student_id.course_detail_ids]
            batch_list = [
                batch.batch_id.id for batch in student_id.course_detail_ids]
            domain += [('course_ids', 'in', course_list),
                       ('batch_ids', 'in', batch_list),
                       ('user_id', '=', int(config_para.value))]

            pager = portal_pager(
                url="/my/academic-calendar/%s" % student_id,
                url_args={'start_date': start_date, 'end_date': end_date,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
            )
        else:
            keep = QueryURL('/my/academic-calendar/', search=search, attrib=attrib_list,
                            order=post.get('order'))

            student = request.env["op.student"].sudo().search(
                [('user_id', '=', request.env.user.id)])

            total = 0
            course_list = [
                course.course_id.id for course in student.course_detail_ids]
            batch_list = [
                batch.batch_id.id for batch in student.course_detail_ids]
            domain += ['|', ('course_ids', '=', False),
                       ('batch_ids', 'in', batch_list),
                       ('user_id', '=', int(config_para.value))]
            pager = portal_pager(
                url="/my/academic-calendar/",
                url_args={'start_date': start_date, 'end_date': end_date,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
            )

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'start_date'):
                search_domain = expression.OR(
                    [search_domain, [('start_date', 'ilike', search)]])
            domain += search_domain

        if groupby == 'course_id':
            order = "course_id, %s" % order

        if student_id:
            academic_calendar_id = request.env['calendar.event'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
        else:
            academic_calendar_id = request.env['calendar.event'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        academic_calendar_lst = [rec for rec in academic_calendar_id]

        if groupby == 'course_id':
            grouped_tasks = [
                request.env['op.session'].sudo().concat(*g)
                for k, g in groupbyelem(academic_calendar_id, itemgetter('course_id'))]
        else:
            grouped_tasks = [academic_calendar_id]
        if student_id:
            val = {
                'date': start_date,
                'events': academic_calendar_lst,
                'page_name': 'academic_calendar',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'current_stud_id': student_id.id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/my/academic-calendar/%s' % student_id,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'grouped_tasks': grouped_tasks,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,

            }
            return request.render(
                "openeducat_core_enterprise.academic_calendar_portal",
                val)
        else:
            values = {
                'date': start_date,
                'events': academic_calendar_lst,
                'page_name': 'academic_calendar',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'current_stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/my/academic-calendar/',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'grouped_tasks': grouped_tasks,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,
            }

            return request.render(
                "openeducat_core_enterprise.academic_calendar_portal",
                values)

    @http.route('/get-calendar-event/data', type='json', auth='user', website=True)
    def get_calendar_event_data_portal(self, stud_id=None, current_timezone=None):
        data = []
        if stud_id:
            student = request.env['op.student'].sudo().search(
                [('id', '=', stud_id)])
        else:
            student = request.env['op.student'].sudo().search(
                [('user_id', '=', request.env.uid)])

        batch_list = [batch.batch_id.id for batch in student.course_detail_ids]
        config_para = request.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'global_calendar_user_id')])
        academic_calendar_events = request.env['calendar.event'].sudo().search(
            ['|', ('course_ids', '=', False),
             ('batch_ids', 'in', batch_list),
             ('user_id', '=', int(config_para.value))])
        for event in academic_calendar_events:
            data.append({
                'title': event.name,
                'start': event.start_date if event.allday
                else event.start.astimezone(abcd(request.env.user.tz)),
                'end': event.stop_date + relativedelta(hours=23, minutes=59, seconds=59)
                if event.allday else event.stop.astimezone(abcd(request.env.user.tz))
            })
        return data

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        user = request.env.user
        values.update({
            'error': {},
            'error_message': [],
        })

        if post:
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {
                    key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update(
                    {key: post[key]
                     for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'zip': values.pop('zipcode', '')})
                values.update({'country_id': int(values.pop('country_id'))})
                values.update({'state_id': (values.pop('state_id')) or False})
                partner.sudo().write(values)
                if user.is_parent:
                    return request.redirect('/my/child')
                else:
                    return request.redirect('/my')
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class OpenEduCatController(http.Controller):

    @http.route('/openeducat_core_enterprise/get_main_dash_data',
                type='json', auth='user')
    def compute_main_dashboard_data(self):
        ser = 0
        es = 0
        mfr = '0:0'
        spr = 0

        adm_ref = request.env['op.admission']
        student_ref = request.env['op.student']
        admission = request.env['ir.model'].search(
            [('model', '=', 'op.admission')])
        if admission:
            total_admsn = adm_ref.search_count([
                ('state', '=', 'done')])
            if total_admsn:
                ser = round(total_admsn * 100 / adm_ref.search_count([]), 2)
                es = adm_ref.search_count([('state', '=', 'done')])
        m_student = student_ref.search_count([('gender', '=', 'm')])
        f_student = student_ref.search_count([('gender', '=', 'f')])
        mfr = str(m_student) + ':' + str(f_student)
        total_faculty = request.env['op.faculty'].search_count([])
        spr = str(m_student + f_student) + ':' + str(total_faculty)
        return {'student_enroll_rate': ser, 'erolled_students': es,
                'mf_ratio': mfr, 'sp_ratio': spr}

    @http.route('/openeducat_core_enterprise/fetch_batch',
                type='json', auth='user')
    def fetch_openeducat_batches(self):
        return {'batch_ids': request.env['op.batch'].search_read(
            [], ['id', 'name'], order='name')}

    @http.route('/openeducat_core_enterprise/compute_openeducat_batch_graph',
                type='json', auth='user')
    def compute_openeducat_batch_graph(self, batch_id):
        data = []
        last_day = datetime.today().replace(
            day=calendar.monthrange(date.today().year,
                                    date.today().month)[1])
        for d in range(1, last_day.day + 1):
            attendance_sheet = request.env['ir.model'].search(
                [('model', '=', 'op.attendance.sheet')])
            if attendance_sheet and batch_id:
                value = request.env['op.attendance.sheet'].search([
                    ('batch_id', '=', int(batch_id)),
                    ('attendance_date', '=',
                     fields.date.today().replace(day=d))])
                data.append({'label': str(d),
                             'value': value and value[0].total_present or 0})
        return data

    @http.route('/openeducat_core_enterprise/get_batch_dashboard_data',
                type='json', auth='user')
    def compute_batch_dashboard_data(self, batch_id):
        tar = 0
        ts = 0
        tbl = 0
        ta = 0
        ir_model_ref = request.env['ir.model']
        op_attn_sheet_ref = request.env['op.attendance.sheet']
        attendance_sheet = ir_model_ref.search([
            ('model', '=', 'op.attendance.sheet')])
        if attendance_sheet and batch_id:
            tarp = op_attn_sheet_ref.search(
                [('batch_id', '=', int(batch_id)),
                 ('attendance_date', '=', fields.date.today())])
            tara = op_attn_sheet_ref.search(
                [('batch_id', '=', int(batch_id)),
                 ('attendance_date', '=', fields.date.today())])
            tar = tarp and str(tarp[0].total_present) or '0'
            tar += ':'
            tar += tara and str(tara[0].total_absent) or '0'
        if batch_id:
            ts = request.env['op.student'].search_count([
                ('course_detail_ids.batch_id', '=', int(batch_id))])
        session = ir_model_ref.search([('model', '=', 'op.session')])
        if session and batch_id:
            tbl = request.env['op.session'].search_count(
                [('batch_id', '=', int(batch_id)),
                 ('start_datetime', '>=',
                  datetime.today().strftime('%Y-%m-%d 00:00:00')),
                 ('start_datetime', '<=',
                  datetime.today().strftime('%Y-%m-%d 23:59:59'))])
        assignment = ir_model_ref.search([('model', '=', 'op.assignment')])
        if assignment and batch_id:
            ta = request.env['op.assignment'].search_count(
                [('batch_id', '=', int(batch_id))])
        return {'tar': tar, 'tbl': tbl, 'ts': ts, 'ta': ta}


PPG = 10  # Record List Per Page


class SubjectRegistrationPortal(CustomerPortal):

    def get_search_domain_subject_registration(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', ('name', 'ilike',
                                    srch), ('batch_id', 'ilike', srch),
                    ('course_id', 'ilike', srch), ('state', 'ilike', srch)
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
        val = {'registartion_count': ''}
        registartion_count = request.env['op.subject.registration'].sudo().search_count(
            [('student_id', '=', student_id)])
        val['registartion_count'] = registartion_count
        return val

    def _prepare_portal_layout_values(self):
        user = request.env.user
        student_id = request.env['op.student'].sudo().search(
            [('user_id', '=', user.id)])
        values = super(SubjectRegistrationPortal,
                       self)._prepare_portal_layout_values()
        registartion_count = request.env['op.subject.registration'].sudo().search_count(
            [('student_id', '=', student_id.id)])
        values['registartion_count'] = registartion_count
        return values

    @http.route(['/subject/registration/',
                 '/subject/registration/<int:student_id>',
                 '/subject/registration/<int:student_id>/page/<int:page>',
                 '/subject/registration/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_student_subject_registration_list(
            self, student_id=None, date_begin=None, date_end=None, page=0,
            search='', search_in='sequence', ppg=False, sortby=None, filterby=None,
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
            'name': {'label': _('Name'), 'order': 'name'},
            'course_id': {'label': _('Course (A to Z)'), 'order': 'course_id'},
            'batch_id': {'label': _('Batch (Z to A)'), 'order': 'batch_id desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'approved': {'label': _('Approved'),
                         'domain': [('state', '=', 'approved')]},
            'rejected': {'label': _('Rejected'),
                         'domain': [('state', '=', 'rejected')]},
            'submitted': {'label': _('Submitted'),
                          'domain': [('state', '=', 'submitted')]},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        searchbar_inputs = {
            'sequence': {'input': 'sequence',
                         'label': Markup(_('Search<span class="nolabel">'
                                           ' (in sequence)</span>'))},
            'state': {'input': 'Status', 'label': _('Search in Status')},
            'course': {'input': 'Course', 'label': _('Search in Course')},
            'batch': {'input': 'Batch', 'label': _('Search in Batch')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'course_id': {'input': 'course_id', 'label': _('Course')},
        }

        domain += self.get_search_domain_subject_registration(
            search, attrib_values)
        if student_id:
            keep = QueryURL('/subject/registration/%s' %
                            student_id, search=search, amenity=attrib_list,
                            order=post.get('order'))

        else:
            keep = QueryURL('/subject/registration/',
                            search=search, amenity=attrib_list,
                            order=post.get('order'))

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'sequence'):
                search_domain = expression.OR([search_domain,
                                               [('name', 'ilike', search), ]])
            if search_in in ('all', 'state'):
                search_domain = expression.OR([search_domain,
                                               [('state', 'ilike', search)]])
            if search_in in ('all', 'course'):
                search_domain = expression.OR([search_domain,
                                               [('course_id', 'ilike', search)]])
            if search_in in ('all', 'batch'):
                search_domain = expression.OR([search_domain,
                                               [('batch_id', 'ilike', search)]])
            domain += search_domain

        student = request.env["op.student"].sudo().search(
            [('user_id', '=', request.env.user.id)])

        if not student_id:
            domain += [('student_id', '=', student.id)]
        else:
            domain += [('student_id', '=', student_id)]

        total = request.env['op.subject.registration'].sudo(
        ).search_count(domain)
        if student_id:
            pager = portal_pager(
                url="/subject/registration/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            pager = portal_pager(
                url="/subject/registration/",
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

            subject_registration_id = request.env[
                'op.subject.registration'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
            attributes = request.env[
                'op.subject.registration'].browse(attributes_ids)

        else:
            subject_registration_id = request.env[
                'op.subject.registration'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
            attributes = request.env[
                'op.subject.registration'].browse(attributes_ids)

        if groupby == 'course_id':
            grouped_tasks = [
                request.env['op.subject.registration'].sudo().concat(*g)
                for k, g in groupbyelem(
                    subject_registration_id, itemgetter('course_id'))]
        else:
            grouped_tasks = [subject_registration_id]

        if student_id:

            val.update({
                'date': date_begin,
                'subject_registration_ids': subject_registration_id,
                'page_name': 'subject_registration',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'search_count': total,
                'default_url': '/subject/registration/%s' % student_id,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attributes': attributes,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,

                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'grouped_tasks': grouped_tasks,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,

            })
            return request.render(
                "openeducat_core_enterprise."
                "portal_student_subject_registration_list",
                val
            )
        else:
            values.update({
                'date': date_begin,
                'subject_registration_ids': subject_registration_id,
                'page_name': 'subject_registration',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'search_count': total,
                'default_url': '/subject/registration/',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attributes': attributes,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'grouped_tasks': grouped_tasks,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,

            })

            return request.render(
                "openeducat_core_enterprise."
                "portal_student_subject_registration_list",
                values
            )

    def check_subject_registration_access(self, reg_id=None):
        registration_id = request.env['op.subject.registration'].sudo().search(
            [('id', '=', reg_id)])

        user = request.env.user
        user_list = []
        count = 0
        for rec in registration_id.student_id:
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

    @http.route(['/subject/registration/data/<int:reistration_id>',
                 '/subject/registration/data/<int:student_id>/<int:reistration_id>'],
                type='http', auth='user', website=True)
    def portal_student_subject_registration_data(
            self, student_id=None, reistration_id=None):

        subject_registration_id = request.env[
            'op.subject.registration'].sudo().search(
            [('id', '=', reistration_id)])

        access_role = self.check_subject_registration_access(
            subject_registration_id.id)
        if access_role is False:
            return Response("[Bad Request]", status=404)

        return request.render(
            "openeducat_core_enterprise."
            "portal_student_subject_registration_data",
            {'subject_register': subject_registration_id,
             'page_name': 'subject_register',
             'student': student_id,
             })

    @http.route(['/subject/registration/create/',
                 '/subject/registration/create/<int:student_id>',
                 '/subject/registration/create/<int:page>'],
                type='http', auth="user", website=True)
    def portal_craete_subject_registration(self, student_id=None, **kw):

        user = request.env.user
        student_id = request.env['op.student'].sudo().search([
            ('user_id', '=', user.id)])

        elective_subjects = request.env['op.subject'].sudo().search(
            [('subject_type', '=', 'elective')])

        course_ids = request.env['op.course'].sudo().search([])

        lms_module = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'openeducat_lms')])

        if lms_module.state != 'uninstalled':
            course_ids = request.env['op.course'].sudo().search(
                [('online_course', '!=', True)])

        batch_ids = request.env['op.batch'].sudo().search([])

        return request.render(
            "openeducat_core_enterprise."
            "openeducat_create_subject_registration",
            {'student_id': student_id,
             'subject_registration_ids': elective_subjects,
             'course_ids': course_ids,
             'batch_ids': batch_ids,
             'page_name': 'subject_reg_form'
             })

    @http.route(['/subject/registration/submit',
                 '/subject/registration/submit/<int:page>'],
                type='http', auth="user", website=True)
    def portal_submit_subject_registration(self, **kw):

        compulsory_subject = request.httprequest. \
            form.getlist('compulsory_subject_ids')
        elective_subject = request.httprequest. \
            form.getlist('elective_subject_ids')

        vals = {
            'student_id': kw['student_id'],
            'course_id': kw['course_id'],
            'batch_id': kw['batch_id'],
            'min_unit_load': kw['min_unit_load'],
            'max_unit_load': kw['max_unit_load'],
            'compulsory_subject_ids': [[6, 0, compulsory_subject]],
            'elective_subject_ids': [[6, 0, elective_subject]],
        }
        registration_id = request.env['op.subject.registration']
        registration_id.sudo().create(vals).action_submitted()

        return request.redirect('/subject/registration/')

    @http.route(['/get/course_data'],
                type='json', auth="none", website=True)
    def get_course_data(self, course_id, **kw):
        batch_list = []
        subject_list = []
        batch_ids = request.env['op.batch'].sudo().search(
            [('course_id', '=', int(course_id))])
        subject_ids = request.env['op.subject'].sudo().search([
            ('course_id', '=', int(course_id))])
        if batch_ids:
            for batch_id in batch_ids:
                batch_list.append({'name': batch_id.name,
                                   'id': batch_id.id})
        if subject_ids:
            for subject_id in subject_ids:
                subject_list.append({'name': subject_id.name,
                                     'id': subject_id.id})
        return {'batch_list': batch_list,
                'subject_list': subject_list}
