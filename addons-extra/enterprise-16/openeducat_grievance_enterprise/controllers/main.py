# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import base64
import datetime
import io
from collections import OrderedDict
from operator import itemgetter

from odoo import _, http
from odoo.http import request
from odoo.tools import groupby as groupbyelem

from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

PPG = 10


class OPGmsController(CustomerPortal):

    # def _prepare_home_portal_values(self, counters):
    #     values = super(OPGmsController, self). \
    #         _prepare_home_portal_values(counters)
    #     user = request.env.user.id
    #     grievance_count = request.env['grievance'].sudo().search_count(
    #         ['|', '|', ('student_id.user_id', '=', user),
    #          ('faculty_id.user_id', '=', user),
    #          ('parent_id.user_id', '=', user), ('state', '!=', 'cancel')])
    #     values['grievance_count'] = grievance_count
    #     return values

    def _prepare_portal_layout_values(self):
        values = super(OPGmsController, self)._prepare_portal_layout_values()
        user = request.env.user.id
        grievance_count = request.env['grievance'].sudo().search_count(
            ['|', '|', ('student_id.user_id', '=', user),
             ('faculty_id.user_id', '=', user),
             ('parent_id.user_id', '=', user), ('state', '!=', 'cancel')])
        values['grievance_count'] = grievance_count
        return values

    def _parent_prepare_portal_layout_values(self, student_id=None):
        val = super(OPGmsController, self)._parent_prepare_portal_layout_values(
            student_id)
        user = request.env.user.id
        grievance_count = request.env['grievance'].sudo().search_count(
            ['|', ('student_id', '=', student_id),
             ('parent_id.user_id', '=', user), ('state', '!=', 'cancel')])
        val['grievance_count'] = grievance_count
        return val

    def get_search_domain_asset(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|',
                    ('grievance_category_id', 'ilike', srch),
                    ('course_id', 'ilike', srch),
                    ('batch_id', 'ilike', srch),
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

    @http.route(['/my/grievances',
                 '/my/grievances/<int:student_id>',
                 '/my/grievances/page/<int:page>',
                 '/my/grievances/<int:student_id>/page/<int:page>'],
                auth='user', website=True, type='http')
    def all_grievances(self, student_id=None, page=0, ppg=False,
                       sortby=None, groupby=None, filterby=None,
                       search_in='all', search='', **kw):

        if student_id:
            val = self._parent_prepare_portal_layout_values(student_id)
        else:
            values = self._prepare_portal_layout_values()
        user = request.env.user.id
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            kw["ppg"] = ppg
        else:
            ppg = PPG
        searchbar_sortings = {
            'id': {'label': _('Newest'), 'order': 'id desc'},
            'grievance_category_id': {'label': _('Category'),
                                      'order': 'grievance_category_id asc'}
        }
        searchbar_filters = {
            'all': {'label': _('All'),
                    'domain': []},
            'draft': {'label': _('Draft'),
                      'domain': [('state', '=', 'draft')]},
            'in_progress': {'label': _('In Review'),
                            'domain': [('state', '=', 'in_review')]},
            'resolve': {'label': _('Resolve'),
                        'domain': [('state', '=', 'resolve')]},
            'submitted': {'label': _('Submitted'),
                          'domain': [('state', '=', 'submitted')]},
            'reject': {'label': _('Reject'),
                       'domain': [('state', '=', 'reject')]},
            'close': {'label': _('close'),
                      'domain': [('state', '=', 'close')]},
        }
        searchbar_inputs = {
            'all': {'input': 'all',
                    'label': _('Search in All')},
            'Category': {'input': 'grievance_category_id',
                         'label': _('grievance category search')},
            'course': {'input': 'course_id',
                       'label': _('search in Course')},
            'batch': {'input': 'batch_id',
                      'label': _('search in Batch')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'category_id': {'input': 'grievance_category_id',
                            'label': _('Category')},
        }

        if not groupby:
            groupby = "none"

        if not sortby:
            sortby = 'id'
        if not filterby:
            filterby = 'all'
        order = searchbar_sortings[sortby]['order']

        if groupby == 'date':
            order = "request_date, %s" % order
        if student_id:
            domain = ['|', ('student_id.id', '=', student_id),
                      ('parent_id.user_id', '=', user), ('state', '!=', 'cancel')]
        else:
            domain = ['|', '|', ('student_id.user_id', '=', user),
                      ('faculty_id.user_id', '=', user),
                      ('parent_id.user_id', '=', user), ('state', '!=', 'cancel')]
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        domain += self.get_search_domain_asset(search, attrib_values)
        domain += searchbar_filters[filterby]['domain']
        grievance_data = request.env['grievance'].sudo().search(domain, order=order)
        if student_id:
            keep = QueryURL('/my/grievances/%s' % student_id,
                            search=search, attrib=attrib_list,
                            sortby=sortby, filterby=filterby, groupby=groupby,
                            search_in=search_in, order=kw.get('order'))
            asset_count = grievance_data.sudo().search_count(domain)
            pager = portal_pager(
                url="/my/grievances/%s" % student_id,
                url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby,
                          'search_in': search_in,
                          'search': search},
                total=asset_count,
                page=page,
                step=ppg
            )
            offset = pager['offset']
            grievance_data = grievance_data[offset: offset + 10]
        else:
            keep = QueryURL('/my/grievances',
                            search=search, attrib=attrib_list, sortby=sortby,
                            filterby=filterby, groupby=groupby,
                            search_in=search_in, order=kw.get('order'))
            asset_count = grievance_data.sudo().search_count(domain)
            pager = portal_pager(
                url="/my/grievances",
                url_args={'sortby': sortby, 'filterby': filterby,
                          'groupby': groupby, 'search_in': search_in,
                          'search': search},
                total=asset_count,
                page=page,
                step=ppg
            )
            offset = pager['offset']
            grievance_data = grievance_data[offset: offset + 10]

        if groupby == 'category_id':
            order = "grievance_category_id, %s" % order

        if groupby == 'category_id':
            categories = [
                request.env['grievance'].sudo().concat(*g)
                for k, g in groupbyelem(
                    grievance_data, itemgetter('grievance_category_id'))]
        else:
            categories = [grievance_data]
        if student_id:
            val.update({
                'user': request.env.user,
                'grievance_data': grievance_data,
                'default_url': '/my/grievances/%s' % student_id,
                'page_name': 'my_grievances',
                'searchbar_sortings': searchbar_sortings,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'search': search,
                'sortby': sortby,
                'groupby': groupby,
                'keep': keep,
                'pager': pager,
                'searchbar_groupby': searchbar_groupby,
                'ppg': ppg,
                'categories': categories,
                'filterby': filterby,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'gms_student_id': student_id,

            })
            return request.render(
                'openeducat_grievance_enterprise.all_grievance', val)

        else:
            values.update({
                'user': request.env.user,
                'default_url': '/my/grievances',
                'grievance_data': grievance_data,
                'page_name': 'my_grievances',
                'searchbar_sortings': searchbar_sortings,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'search': search,
                'sortby': sortby,
                'groupby': groupby,
                'searchbar_groupby': searchbar_groupby,
                'keep': keep,
                'pager': pager,
                'ppg': ppg,
                'categories': categories,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,

            })
            return request.render(
                'openeducat_grievance_enterprise.all_grievance', values)

    @http.route(['/my/grievance/detail/<model("grievance"):grievances>',
                 '/my/grievance/detail/<int:gms_student_id>/'
                 '<model("grievance"):grievances>'],
                auth='user', website=True,
                type='http')
    def my_grievance_details(self, gms_student_id=None, grievances=None, **post):
        values = self._prepare_portal_layout_values()
        login_user = self.login_user(grievances)
        user = request.env.user
        grievances_parent_data = request.env['grievance'].sudo().search([])
        parent_grievance_list = []

        for parent_grievance in grievances_parent_data.grievance_parent_id:
            parent_grievance_list.append(parent_grievance.id)
        if gms_student_id:
            values.update({
                'gms_student_id': gms_student_id,
                'page_name': 'my_grievance_details',
                'grievance_data': grievances.sudo(),
                'user_id': user,
                'grievance_parent_data': parent_grievance_list,
            })
        else:
            values.update({
                'page_name': 'my_grievance_details',
                'grievance_data': grievances.sudo(),
                'user_id': user,
                'grievance_parent_data': parent_grievance_list
            })

        if gms_student_id:
            return request.render(
                'openeducat_grievance_enterprise.portal_grievance_details', values)
        else:
            if login_user:
                if grievances.state == 'cancel':
                    return request.redirect('/my/grievance-access-denied')
                else:
                    return request.render(
                        'openeducat_grievance_enterprise.portal_grievance_details',
                        values)
            else:
                return request.redirect('/my/grievance-access-denied')

    @http.route(['/my/grievance/grievance-form',
                 '/my/grievance/grievance-form/<int:gms_student_id>',
                 '/my/grievance/grievance-edit/<model("grievance"):grievances>',
                 '/my/grievance/grievance-edit/<int:gms_student_id>/'
                 '<model("grievance"):grievances>',
                 '/my/grievance/appeal/<model("grievance"):appeal_grievances>',
                 '/my/grievance/appeal/<int:gms_student_id>/'
                 '<model("grievance"):appeal_grievances>'],
                auth='user', website=True, type='http')
    def grievance_form(self, grievances=None, gms_student_id=None,
                       appeal_grievances=None, **post):
        login_user = self.login_user(grievances)
        user = request.env.user
        grievances_parent_data = request.env['grievance'].sudo().search([])
        parent_grievance_list = []

        for parent_grievance in grievances_parent_data.grievance_parent_id:
            parent_grievance_list.append(parent_grievance.id)

        # grievance_data = request.env['grievance'].sudo().search([])
        student = request.env['op.student'].sudo().search(
            [('user_id', '=', request.env.user.id)])

        faculty = request.env['op.faculty'].sudo().search(
            [('user_id', '=', request.env.user.id)])

        parent = request.env['op.parent'].sudo().search(
            [('user_id', '=', request.env.user.id)])

        course_ids = request.env['op.course'].sudo().search([])
        academic_year_ids = request.env['op.academic.year'].sudo().search([])
        grievance_category_ids = request.env['grievance.category']. \
            sudo().search([('parent_id', '!=', False)])
        attachment_obj = request.env['ir.attachment'].sudo().search([])
        grievance_data = request.env['grievance'].sudo().search([])

        values = {
            'user': user,
            'student': student,
            'faculty': faculty,
            'course_ids': course_ids,
            'academic_year_ids': academic_year_ids,
            'grievance_category_ids': grievance_category_ids,
            'parent': parent,
            'grievance_data': grievance_data,
            'page_name': 'grievance_form',
        }

        if appeal_grievances:
            appeal_grievance_user = self.login_user(appeal_grievances)
            appeal_grievance_data = request.env['grievance']. \
                sudo().browse(appeal_grievances.id)
            if appeal_grievances:
                values.update({
                    'grievance_parent_id': appeal_grievance_data,
                })

        if gms_student_id:
            gms_student_id = request.env['op.student'].sudo().browse(gms_student_id)
            values.update({
                'gms_student_id': gms_student_id,
            })

        if post:
            if post.get('grievance_parent_id'):
                appeal_grievance_data = request.env['grievance'].sudo().search(
                    [('id', '=', int(post.get('grievance_parent_id')))])
                grievance_category_id = request.env['grievance.category'].sudo().browse(
                    appeal_grievance_data.grievance_category_id.id)

            else:
                grievance_category_id = request.env['grievance.category'].sudo().browse(
                    int(post.get('grievance_category_id')))

            record = request.env['grievance.team'].sudo().search(
                [('grievance_category_id', '=', grievance_category_id.id)])

            if record:
                for rec in record:
                    grievance_team_id = rec.id
            else:
                grievance_team_id = False

            records = {
                'grievance_for': post.get('grievance_for'),
                'subject': post.get('subject'),
                'faculty_id': faculty.id or False,
                'parent_id': parent.id or False,
                'description': post.get('description'),
                'grievance_category_id': grievance_category_id.id,
                'grievance_team_id': grievance_team_id,
                'created_date': datetime.date.today(),
            }
            if post.get('grievance_parent_id'):
                appeal_grievance_data = request.env['grievance']. \
                    sudo().browse(int(post.get('grievance_parent_id')))
                records.update({
                    'grievance_parent_id': appeal_grievance_data.id,
                    'is_appeal': True,
                    'state': 'submitted',
                    'grievance_category_id':
                        appeal_grievance_data.grievance_category_id.id
                })

            if gms_student_id:
                if grievance_category_id.is_academic is True:
                    records.update({
                        'student_id': gms_student_id.id,
                        'course_id': request.env['op.course'].sudo().browse(
                            int(post.get('course_id'))).id,
                        'batch_id': request.env['op.batch'].sudo().browse(
                            int(post.get('batch_id'))).id,
                        'academic_year_id':
                            request.env['op.academic.year'].sudo().browse(
                                int(post.get('academic_year_id'))).id,
                        'academic_term_id':
                            request.env['op.academic.term'].sudo().browse(
                                int(post.get('academic_term_id'))).id,
                    })
                else:
                    records.update({
                        'student_id': gms_student_id.id,
                        'course_id': False,
                        'batch_id': False,
                        'academic_year_id': False,
                        'academic_term_id': False,
                    })
            else:
                if grievance_category_id.is_academic is True:
                    records.update({
                        'student_id': student.id or False,
                        'course_id': request.env['op.course'].sudo().browse(
                            int(post.get('course_id'))).id,
                        'batch_id': request.env['op.batch'].sudo().browse(
                            int(post.get('batch_id'))).id,
                        'academic_year_id':
                            request.env['op.academic.year'].sudo().browse(
                                int(post.get('academic_year_id'))).id,
                        'academic_term_id':
                            request.env['op.academic.term'].sudo().browse(
                                int(post.get('academic_term_id'))).id,
                    })
                else:
                    records.update({
                        'student_id': student.id or False,
                        'course_id': False,
                        'batch_id': False,
                        'academic_year_id': False,
                        'academic_term_id': False,
                    })

        if not grievances:
            if post:
                grievance = request.env['grievance'].sudo().create(records)
                if post.get('file'):
                    for name in request.httprequest.files.getlist('file'):
                        attach_values = {
                            'name': name.filename,
                            'res_model': 'grievance',
                            'res_id': grievance,
                            'public': True,
                            'type': 'binary',
                            'datas': base64.encodebytes(name.read()),
                        }
                        attachment_obj.sudo().create(attach_values)
                else:
                    None
                if gms_student_id:
                    url = '/my/grievances/%s' % str(gms_student_id.id)
                    return request.redirect(url)
                else:
                    return request.redirect('/my/grievances')

            if gms_student_id:
                if appeal_grievances:
                    if appeal_grievances.id not in parent_grievance_list:
                        return request.render(
                            'openeducat_grievance_enterprise.grievance_registration',
                            values)
                    else:
                        return request.redirect('/my/grievance-access-denied')
                else:
                    return request.render(
                        'openeducat_grievance_enterprise.grievance_registration',
                        values)
            else:
                if appeal_grievances:
                    if appeal_grievance_user and \
                            appeal_grievances.id not in parent_grievance_list:
                        return request.render(
                            'openeducat_grievance_enterprise.grievance_registration',
                            values)
                    else:
                        return request.redirect('/my/grievance-access-denied')
                else:
                    return request.render(
                        'openeducat_grievance_enterprise.grievance_registration',
                        values)
        else:
            grievance_record_data = request.env['grievance'].sudo(). \
                browse(grievances.id)

            values.update({'grievances': grievance_record_data})

            attachment_obj1 = request.env['ir.attachment'].sudo().search(
                [('res_id', '=', grievances.id), ('res_model', '=', 'grievance')])
            attachment_obj1.unlink()

            if post:
                if post.get('is_state_change'):
                    records.update({
                        'state': 'submitted'
                    })
                    template = request.env.ref(
                        'openeducat_grievance_enterprise.mail_template_gms',
                        raise_if_not_found=False)
                    template.sudo().send_mail(grievances.id, force_send=True)
                    grievance_record_data.update(records)
                else:
                    grievance_record_data.update(records)
                if post.get('file'):
                    for name in request.httprequest.files.getlist('file'):
                        attach_values = {
                            'name': name.filename,
                            'res_model': 'grievance',
                            'res_id': grievance_record_data,
                            'public': True,
                            'type': 'binary',
                            'datas': base64.encodebytes(name.read()),
                        }
                        attachment_obj.sudo().create(attach_values)
                else:
                    None
                if gms_student_id:
                    url = '/my/grievances/%s' % str(gms_student_id.id)
                    return request.redirect(url)
                else:
                    return request.redirect('/my/grievances')

            if gms_student_id:
                return request.render(
                    'openeducat_grievance_enterprise.grievance_edit', values)
            else:
                if login_user and grievances.state == 'draft':
                    return request.render(
                        'openeducat_grievance_enterprise.grievance_edit', values)
                else:
                    return request.redirect('/my/grievance-access-denied')

    @http.route(['/get/grievance/course_data'],
                type='json', auth="user", website=True)
    def get_course_grievance_data(self, course_id, **kw):
        batch_list = []
        batch_ids = request.env['op.batch'].sudo().search(
            [('course_id', '=', int(course_id))])

        if batch_ids:
            for batch_id in batch_ids:
                batch_list.append({'name': batch_id.name,
                                   'id': batch_id.id})
        return {'batch_list': batch_list}

    @http.route(['/get/academic_term_data'],
                type='json', auth="user", website=True)
    def get_academic_year_data(self, academic_year_id, **kw):
        academic_term_list = []
        term_ids = request.env['op.academic.term'].sudo().search(
            [('academic_year_id', '=', int(academic_year_id))])

        if term_ids:
            for term_id in term_ids:
                academic_term_list.append({'name': term_id.name,
                                           'id': term_id.id})
        return {'academic_term_list': academic_term_list}

    @http.route(['/my/grievance/submit/<model("grievance"):grievances>',
                 '/my/grievance/submit/<int:gms_student_id>/'
                 '<model("grievance"):grievances>'],
                auth='user', website=True)
    def submit_state_grievance(self, gms_student_id=None, grievances=None):
        login_user = self.login_user(grievances)
        if gms_student_id and grievances.state not in ['cancel', 'reject', 'close']:
            grievances.submitted_progressbar()
            template = request.env.ref(
                'openeducat_grievance_enterprise.mail_template_gms',
                raise_if_not_found=False)
            template.sudo().send_mail(grievances.id, force_send=True)
            url = '/my/grievance/detail/%s/%s' % (str(gms_student_id), slug(grievances))
            return request.redirect(url)

        else:
            if login_user and grievances.state not in ['cancel', 'reject', 'close']:
                grievances.submitted_progressbar()
                template = request.env.ref(
                    'openeducat_grievance_enterprise.mail_template_gms',
                    raise_if_not_found=False)
                template.sudo().send_mail(grievances.id, force_send=True)
                url = '/my/grievance/detail/%s' % slug(grievances)
                return request.redirect(url)
            else:
                return request.redirect('/my/grievance-access-denied')

    @http.route(['/my/grievance/cancel/<model("grievance"):grievances>',
                 '/my/grievance/cancel/<int:gms_student_id>/'
                 '<model("grievance"):grievances>'],
                auth='user', website=True)
    def cancel_state_grievance(self, gms_student_id=None, grievances=None):
        login_user = self.login_user(grievances)
        if gms_student_id and grievances.state not in ['submitted', 'reject', 'close']:
            grievances.cancel_progressbar()
            url = '/my/grievances/%s' % str(gms_student_id)
            return request.redirect(url)
        else:
            if login_user and grievances.state not in ['submitted', 'reject', 'close']:
                grievances.cancel_progressbar()
                return request.redirect('/my/grievances')
            else:
                return request.redirect('/my/grievance-access-denied')

    @http.route(['/attachment/download/<int:attachment_id>'],
                type='http', auth='user', website=True)
    def download_submission_attachment(self, attachment_id):

        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"]
        )
        if attachment:
            attachment = attachment[0]
        res_id = attachment['res_id']
        grievance_id = request.env['grievance'].sudo().browse(res_id)

        if grievance_id:
            if attachment["type"] == "url":
                if attachment["url"]:
                    return http.redirect_with_hash(attachment["url"])
                else:
                    return request.not_found()
            elif attachment["datas"]:
                data = io.BytesIO(base64.standard_b64decode(
                    attachment["datas"]))
                return http.Stream(
                    data, filename=attachment['name'], as_attachment=True)
            else:
                return request.not_found()

    @http.route(['/my/grievance/satisfied/<model("grievance"):grievances>',
                 '/my/grievance/satisfied/<int:gms_student_id>/'
                 '<model("grievance"):grievances>'],
                auth='user', website=True)
    def satisfied_grievance(self, gms_student_id=None, grievances=None):
        login_user = self.login_user(grievances)
        if grievances.is_satisfied is False:
            if gms_student_id:
                grievances.update({
                    'is_satisfied': 'yes',
                })
                url = '/my/grievance/detail/%s/%s' % (str(gms_student_id),
                                                      slug(grievances))
                return request.redirect(url)
            else:
                if login_user and grievances.state == 'resolve':
                    grievances.update({
                        'is_satisfied': 'yes',
                    })
                    url = '/my/grievance/detail/%s' % slug(grievances)
                    return request.redirect(url)
                else:
                    return request.redirect('/my/grievance-access-denied')
        else:
            return request.redirect('/my/grievance-access-denied')

    @http.route(['/my/grievance/not-satisfied/<model("grievance"):grievances>',
                 '/my/grievance/not-satisfied/<int:gms_student_id>/'
                 '<model("grievance"):grievances>'],
                auth='user', website=True)
    def not_satisfied_grievance(self, gms_student_id=None, grievances=None):
        login_user = self.login_user(grievances)
        if grievances.is_satisfied is False or grievances.is_satisfied != 'yes':
            if gms_student_id:
                grievances.update({
                    'is_satisfied': 'no',
                })
                url = '/my/grievance/detail/%s/%s' % (str(gms_student_id),
                                                      slug(grievances))
                return request.redirect(url)
            else:
                if login_user and grievances.state == 'resolve':
                    grievances.update({
                        'is_satisfied': 'no',
                    })

                    url = '/my/grievance/detail/%s' % slug(grievances)
                    return request.redirect(url)
                else:
                    return request.redirect('/my/grievance-access-denied')
        else:
            return request.redirect('/my/grievance-access-denied')

    @http.route(['/my/grievance-access-denied'],
                auth='user', website=True)
    def grievance_access_denied(self):
        return request.render(
            'openeducat_grievance_enterprise.grievance_access_denied')

    def login_user(self, grievances):
        if grievances:
            user = request.env.user
            student_rec = request.env['op.student'].sudo().search(
                [('id', '=', grievances.student_id.id)])
            faculty_rec = request.env['op.faculty'].sudo().search(
                [('id', '=', grievances.faculty_id.id)])
            parent_rec = request.env['op.parent'].sudo().search(
                [('id', '=', grievances.parent_id.id)])

            if parent_rec.user_id.id == user.id:
                login_user = parent_rec.user_id
            elif faculty_rec.user_id.id == user.id:
                login_user = faculty_rec.user_id
            elif student_rec.user_id.id == user.id:
                login_user = student_rec.user_id
            else:
                login_user = None
            return login_user
        else:
            return None
