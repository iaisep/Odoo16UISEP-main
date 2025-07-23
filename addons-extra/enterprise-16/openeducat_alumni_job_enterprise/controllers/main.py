# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from collections import OrderedDict
from operator import itemgetter

import dateutil.parser
from markupsafe import Markup

from odoo import _, http
from odoo.http import request
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

PPG = 10  # record per page


class AlumaniJobPost(CustomerPortal):

    @http.route(['/alumni/job',
                 '/alumni/job/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_alumni_job_post(self, **kw):
        emp_type = request.env['op.job.type'].sudo().search([])
        skill_obj = request.env['op.student.skill.name'].sudo().search([])
        skill_ids = [skill_id for skill_id in skill_obj]
        country_id = request.env['res.country'].sudo().search([])
        state_id = request.env['res.country.state'].sudo().search([])

        return request.render(
            "openeducat_alumni_job_enterprise.portal_student_alumni_job",
            {'emp_type': emp_type,
             'skill_obj': skill_ids,
             'country_obj': country_id,
             'state_obj': state_id})

    @http.route(['/alumni/job/submit',
                 '/alumni/job/submit/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_alumni_job_post_submit(self, **kw):

        start_date = dateutil.parser.parse(
            kw['start_date']).strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = dateutil.parser.parse(
            kw['end_date']).strftime(DEFAULT_SERVER_DATE_FORMAT)

        vals = {
            'job_post': kw['job_post'],
            'salary_from': kw['salary_from'],
            'salary_upto': kw['salary_upto'],
            'street': kw['street'],
            'street2': kw['street'],
            'city': kw['city'],
            'start_date': start_date,
            'end_date': end_date,
            'created_by': kw['created_by'],
            'payable_at': kw['payable_at'],
            'expected_employees': kw['expected_employees'],
            'description': kw['description'],
            'employment_type': kw['employment_type'],
            'zip': kw['zip'],
            'country_id': kw['country_id'],
            # 'state_id': kw['state_id'],
            'skill_ids': [
                [6, 0, request.httprequest.form.getlist('skill_ids')]
            ]
        }
        request.env['op.job.post'].sudo().create(vals)
        return request.redirect("/alumni/job/list")

    def _prepare_portal_layout_values(self):
        values = super(AlumaniJobPost, self)._prepare_portal_layout_values()
        alumni_count = request.env['op.job.post'].sudo().search_count([])
        values['alumni_count'] = alumni_count
        return values

    def _parent_prepare_portal_layout_values(self, student_id=None):
        val = super(AlumaniJobPost, self). \
            _parent_prepare_portal_layout_values(student_id)
        alumni_count = request.env['op.job.post'].sudo().search_count([])
        val['alumni_count'] = alumni_count
        return val

    def get_search_domain_alumni_job(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', '|', '|', '|', '|', ('name', 'ilike', srch),
                    ('job_post', 'ilike', srch), ('salary_from', 'ilike', srch),
                    ('salary_upto', 'ilike', srch), ('start_date', 'ilike', srch),
                    ('end_date', 'ilike', srch), ('created_by', 'ilike', srch),
                    ('payable_at', 'ilike', srch)
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

    @http.route(['/alumni/job/list',
                 '/alumni/job/list/<int:student_id>',
                 '/alumni/job/list/page/<int:page>',
                 '/alumni/job/list/<int:student_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_alumni_job_post_list(
            self, student_id=None, date_begin=None, date_end=None, page=0,
            search='', ppg=False, sortby=None, filterby=None,
            search_in='sequence', groupby='created_by', **post):

        if student_id:
            val = self._parent_prepare_portal_layout_values(student_id)
        else:
            values = self._prepare_portal_layout_values()

        user = request.env.user
        user_id = user.id

        student = request.env['op.student'].sudo().search(
            [('user_id', '=', user_id)])
        alumni_student = student.alumni_boolean

        if alumni_student is True:

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
                'payable_at': {'label': _('Payable At'), 'order': 'payable_at'},
                'end_date': {'label': _('End Date'), 'order': 'end_date desc'},
                'start_date': {'label': _('Start Date'), 'order': 'start_date'},
                'states': {'label': _('Status'), 'order': 'states'},
            }

            searchbar_filters = {
                'all': {'label': _('All'), 'domain': []},
                'created_by alumni': {'label': _('Created By Alumni'),
                                      'domain': [('created_by', '=', 'alumni')]},
                'created_by placement': {'label': _('Created By Placement'),
                                         'domain': [('created_by', '=', 'placement')]},
                'payable_at Monthly': {'label': _('Payable At Monthly'),
                                       'domain': [('payable_at', '=', 'monthly')]},
                'payable_at Weekly': {'label': _('Payable At Weekly'),
                                      'domain': [('payable_at', '=', 'weekly')]},
                'payable_at Yearly': {'label': _('Payable At Yearly'),
                                      'domain': [('payable_at', '=', 'yearly')]},
            }

            if not filterby:
                filterby = 'all'
            domain = searchbar_filters[filterby]['domain']

            if not sortby:
                sortby = 'name'
            order = searchbar_sortings[sortby]['order']

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
            attrib_set = {v[1] for v in attrib_values}

            searchbar_inputs = {
                'sequence': {'input': 'sequence',
                             'label': Markup(_('Search<span class="nolabel"> '
                                               '(in sequence)</span>'))},
                'created_by': {'input': 'Created By',
                               'label': _('Search in Created By')},
                'salary_from': {'input': 'Salery From',
                                'label': _('Search in Salary From')},
                'salary_upto': {'input': 'Salary Upto',
                                'label': _('Search in Salary Upto')},
                'start_date': {'input': 'Start Date',
                               'label': _('Search in Start Date')},
                'end_date': {'input': 'Start Date',
                             'label': _('Search in End Date')},
                'job_post': {'input': 'Job Post',
                             'label': _('Search in Job Post')},
                'payable_at': {'input': 'Payable At',
                               'label': _('Search in Payable At')},
                'all': {'input': 'all', 'label': _('Search in All')},
            }
            searchbar_groupby = {
                'none': {'input': 'none', 'label': _('None')},
                'created_by': {'input': 'created_by', 'label': _('Created By')},
            }

            keep = QueryURL('/alumni/job/list',
                            search=search, amenity=attrib_list, order=post.get('order'))

            domain += self.get_search_domain_alumni_job(search, attrib_values)

            if search:
                post["search"] = search
            if attrib_list:
                post['attrib'] = attrib_list

            if search and search_in:
                search_domain = []
                if search_in in ('all', 'sequence'):
                    search_domain = expression.OR(
                        [search_domain, [('name', 'ilike', search)]])
                if search_in in ('all', 'created_by'):
                    search_domain = expression.OR(
                        [search_domain, [('created_by', 'ilike', search)]])
                if search_in in ('all', 'salary_from'):
                    search_domain = expression.OR(
                        [search_domain, [('salary_from', 'ilike', search)]])
                if search_in in ('all', 'salary_upto'):
                    search_domain = expression.OR(
                        [search_domain, [('salary_upto', 'ilike', search)]])
                if search_in in ('all', 'start_date'):
                    search_domain = expression.OR(
                        [search_domain, [('start_date', 'ilike', search)]])
                if search_in in ('all', 'end_date'):
                    search_domain = expression.OR(
                        [search_domain, [('end_date', 'ilike', search)]])
                if search_in in ('all', 'job_post'):
                    search_domain = expression.OR(
                        [search_domain, [('job_post', 'ilike', search)]])
                if search_in in ('all', 'payable_at'):
                    search_domain = expression.OR(
                        [search_domain, [('payable_at', 'ilike', search)]])
                domain += search_domain

            domain += [('create_uid', '=', user_id)]

            total = request.env['op.job.post'].sudo().search_count(domain)

            pager = portal_pager(
                url="/alumni/job/list",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search_in': search_in,
                          'search': search},
                total=total,
                page=page,
                step=self._items_per_page
            )
            alumni_student_id = request.env['op.job.post']. \
                sudo().search(domain, order=order,
                              limit=self._items_per_page,
                              offset=pager['offset'])

            if groupby == 'created_by':
                order = "created_by, %s" % order

            alumni_id = request.env['op.job.post'].sudo().search(
                [], order=order, limit=self._items_per_page,
                offset=pager['offset'])

            alumni_other_id = set(alumni_id).difference(alumni_student_id)

            if groupby == 'created_by':
                grouped_tasks_student = [
                    request.env['op.job.post'].sudo().concat(*g)
                    for k, g in groupbyelem(
                        alumni_student_id, itemgetter('created_by'))]
            else:
                grouped_tasks_student = [alumni_student_id]
            if groupby == 'created_by':
                grouped_tasks = [
                    request.env['op.job.post'].sudo().concat(*g)
                    for k, g in groupbyelem(alumni_other_id, itemgetter('created_by'))]
            else:
                grouped_tasks = [alumni_other_id]

            if student_id:

                student_access = self.get_student(student_id=student_id)
                if student_access is False:
                    return request.render('website.404')

                val.update({
                    'date': date_begin,
                    'alumni': alumni_student_id,
                    'alumni_student': alumni_student,
                    'alumni_others': alumni_other_id,
                    'page_name': 'Alumni_List',
                    'pager': pager,
                    'ppg': ppg,
                    'keep': keep,
                    'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                    'filterby': filterby,
                    'default_url': '/alumni/job/list',
                    'searchbar_sortings': searchbar_sortings,
                    'sortby': sortby,
                    'attrib_values': attrib_values,
                    'attrib_set': attrib_set,
                    'searchbar_inputs': searchbar_inputs,
                    'search_in': search_in,
                    'grouped_tasks': grouped_tasks,
                    'grouped_tasks_student': grouped_tasks_student,
                    'searchbar_groupby': searchbar_groupby,
                    'groupby': groupby,

                })
                return request.render(
                    "openeducat_alumni_job_enterprise.Alumni_posted_job_list", val)
            else:

                values.update({
                    'date': date_begin,
                    'alumni': alumni_student_id,
                    'alumni_student': alumni_student,
                    'alumni_others': alumni_other_id,
                    'page_name': 'Alumni_List',
                    'pager': pager,
                    'ppg': ppg,
                    'keep': keep,
                    'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                    'filterby': filterby,
                    'default_url': '/alumni/job/list',
                    'searchbar_sortings': searchbar_sortings,
                    'sortby': sortby,
                    'attrib_values': attrib_values,
                    'attrib_set': attrib_set,
                    'searchbar_inputs': searchbar_inputs,
                    'search_in': search_in,
                    'grouped_tasks': grouped_tasks,
                    'grouped_tasks_student': grouped_tasks_student,
                    'searchbar_groupby': searchbar_groupby,
                    'groupby': groupby,

                })
                return request.render(
                    "openeducat_alumni_job_enterprise.Alumni_posted_job_list", values)

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
            'payable_at': {'label': _('Payable At'), 'order': 'payable_at'},
            'end_date': {'label': _('End Date'), 'order': 'end_date desc'},
            'start_date': {'label': _('Start Date'), 'order': 'start_date'},
            'states': {'label': _('Status'), 'order': 'states'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'created_by alumni': {'label': _('Created By Alumni'),
                                  'domain': [('created_by', '=', 'alumni')]},
            'created_by placement': {'label': _('Created By Placement'),
                                     'domain': [('created_by', '=', 'placement')]},
            'payable_at Monthly': {'label': _('Payable At Monthly'),
                                   'domain': [('payable_at', '=', 'monthly')]},
            'payable_at Weekly': {'label': _('Payable At Weekly'),
                                  'domain': [('payable_at', '=', 'weekly')]},
            'payable_at Yearly': {'label': _('Payable At Yearly'),
                                  'domain': [('payable_at', '=', 'yearly')]},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        searchbar_inputs = {
            'sequence': {'input': 'sequence',
                         'label': Markup(_('Search<span class="nolabel">'
                                           ' (in sequence)</span>'))},
            'created_by': {'input': 'Created By',
                           'label': _('Search in Created By')},
            'salary_from': {'input': 'Salery From',
                            'label': _('Search in Salary From')},
            'salary_upto': {'input': 'Salary Upto',
                            'label': _('Search in Salary Upto')},
            'start_date': {'input': 'Start Date',
                           'label': _('Search in Start Date')},
            'end_date': {'input': 'Start Date',
                         'label': _('Search in End Date')},
            'job_post': {'input': 'Job Post',
                         'label': _('Search in Job Post')},
            'payable_at': {'input': 'Payable At',
                           'label': _('Search in Payable At')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'created_by': {'input': 'created_by', 'label': _('Created By')},
        }

        domain += self.get_search_domain_alumni_job(search, attrib_values)

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'sequence'):
                search_domain = expression.OR(
                    [search_domain, [('name', 'ilike', search)]])
            if search_in in ('all', 'created_by'):
                search_domain = expression.OR(
                    [search_domain, [('created_by', 'ilike', search)]])
            if search_in in ('all', 'salary_from'):
                search_domain = expression.OR(
                    [search_domain, [('salary_from', 'ilike', search)]])
            if search_in in ('all', 'salary_upto'):
                search_domain = expression.OR(
                    [search_domain, [('salary_upto', 'ilike', search)]])
            if search_in in ('all', 'start_date'):
                search_domain = expression.OR(
                    [search_domain, [('start_date', 'ilike', search)]])
            if search_in in ('all', 'end_date'):
                search_domain = expression.OR(
                    [search_domain, [('end_date', 'ilike', search)]])
            if search_in in ('all', 'job_post'):
                search_domain = expression.OR(
                    [search_domain, [('job_post', 'ilike', search)]])
            if search_in in ('all', 'payable_at'):
                search_domain = expression.OR(
                    [search_domain, [('payable_at', 'ilike', search)]])
            domain += search_domain

        if student_id:
            keep = QueryURL('/alumni/job/list/%s' % student_id,
                            search=search, amenity=attrib_list,
                            order=post.get('order'))
            total = request.env['op.job.post'].sudo().search_count(domain)

            pager = portal_pager(
                url="/alumni/job/list/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search_in': search_in,
                          'search': search},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/alumni/job/list', search=search,
                            amenity=attrib_list, order=post.get('order'))
            total = request.env['op.job.post'].sudo().search_count(domain)

            pager = portal_pager(
                url="/alumni/job/list",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search_in': search_in,
                          'search': search},
                total=total,
                page=page,
                step=ppg
            )

        if groupby == 'created_by':
            order = "created_by, %s" % order

        alumni_obj = request.env['op.job.post'].sudo().search(
            domain, order=order, limit=ppg, offset=pager['offset'])

        if groupby == 'created_by':
            grouped_tasks = [request.env['op.job.post'].sudo().concat(*g) for k, g in
                             groupbyelem(alumni_obj, itemgetter('created_by'))]
        else:
            grouped_tasks = [alumni_obj]

        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')

            val.update({
                'date': date_begin,
                'alumni': alumni_obj,
                'page_name': 'Alumni_List',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/alumni/job/list/%s' % student_id,
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
                "openeducat_alumni_job_enterprise.portal_student_alumni_job_list",
                val)
        else:
            values.update({
                'date': date_begin,
                'alumni': alumni_obj,
                'page_name': 'Alumni_List',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/alumni/job/list',
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
                "openeducat_alumni_job_enterprise.portal_student_alumni_job_list",
                values)

    @http.route(['/alumni/job/details/<int:alumni_id>',
                 '/alumni/job/details/<int:student_id>/<int:alumni_id>',
                 '/alumni/job/details/<int:alumni_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_alumni_job_post_list_details(
            self, student_id=None, alumni_id=None, **kw):
        alumni_obj = request.env['op.job.post'].sudo().search(
            [('id', '=', alumni_id)])

        return request.render(
            "openeducat_alumni_job_enterprise.porta_alumni_list_details",
            {'alumni_data': alumni_obj,
             'student': student_id,
             'page_name': 'alumni_job_info', })

    @http.route(['/alumni/job/delete/<int:alumni>',
                 '/alumni/job/delete/page/<int:page>'],
                type='http', auth="user", website=True)
    def delete_alumni(self, alumni):
        delete_id = request.env['op.job.post'] \
            .sudo().search([('id', '=', alumni)])
        delete_id.unlink()
        return request.redirect('/alumni/job/list')

    @http.route(['/alumni/job/data/<int:alumni_id>',
                 '/alumni/job/data/<int:alumni_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_alumni_job_post_list_data(self, alumni_id, **kw):
        alumni_obj = request.env['op.job.post'].sudo().search(
            [('id', '=', alumni_id)])

        emp_type = request.env['op.job.type'].sudo().search([])
        skill_obj = request.env['op.student.skill.name'].sudo().search([])
        skill_ids = [skill_id for skill_id in skill_obj]
        country_id = request.env['res.country'].sudo().search([])
        state_id = request.env['res.country.state'].sudo().search([])

        return request.render(
            "openeducat_alumni_job_enterprise.portal_alumni_job_list_data",
            {'alumni_data': alumni_obj,
             'emp_type': emp_type,
             'skill_obj': skill_ids,
             'country_obj': country_id,
             'state_obj': state_id})

    @http.route(['/alumni/job/update/<int:alumni_id>',
                 '/alumni/job/update/<int:alumni_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_alumni_job_post_data_edit(self, alumni_id, **kw):
        skills_data = request.httprequest.form.getlist('skill_ids')
        vals = {
            'job_post': kw['job_post'],
            'salary_from': kw['salary_from'],
            'salary_upto': kw['salary_upto'],
            'street': kw['street'],
            'street2': kw['street'],
            'city': kw['city'],
            'start_date': kw['start_date'],
            'end_date': kw['end_date'],
            'created_by': kw['created_by'],
            'payable_at': kw['payable_at'],
            'expected_employees': kw['expected_employees'],
            'description': kw['description'],
            'employment_type': kw['employment_type'],
            'zip': kw['zip'],
            'country_id': kw['country_id'],
            # 'state_id': kw['state_id'],
            'skill_ids': [(6, 0, [int(g) for g in skills_data])]
        }

        alumni_post_id = request.env['op.job.post'].sudo().search(
            [('id', '=', alumni_id)]
        )
        alumni_post_id.sudo().write(vals)
        return request.redirect("/alumni/job/list")

    @http.route(['/get/country_data'],
                type='json', auth="none", website=True)
    def get_country_data(self, country_id, **kw):
        state_list = []
        state_ids = request.env['res.country.state'].sudo().search(
            [('country_id', '=', int(country_id))])

        for i in state_ids:
            state_list.append({'id': i.id, 'name': i.name})

        return {'state_list': state_list}
