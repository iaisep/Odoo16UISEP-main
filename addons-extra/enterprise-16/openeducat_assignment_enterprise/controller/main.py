# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import base64
import io
from collections import OrderedDict
from datetime import datetime
from operator import itemgetter

import dateutil.parser
from markupsafe import Markup

from odoo import _, http
from odoo.http import Response, request
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

PPG = 10  # record list


class SubmitAssignment(CustomerPortal):

    @http.route(['/assignment/submit/<int:assignment_id>',
                 '/assignment/submit/<int:student_id>/<int:assignment_id>',
                 '/assignment/submit/<int:assignment_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_submit_assignment(self, assignment_id=None, student_id=None, **kw):
        user = request.env.user
        assignment_list = []

        if not student_id:
            student = request.env['op.student'].sudo().search([
                ('user_id', '=', user.id)])
            for assignment in student.allocation_ids:
                if assignment.state not in ['finish', 'draft', 'cancel'] \
                        and assignment.id == assignment_id:
                    assignment_list.append(assignment)
        else:
            student = request.env['op.student'].sudo().search([
                ('id', '=', student_id)])
            for assignment in student.allocation_ids:
                if assignment.state not in ['finish']:
                    assignment_list.append(assignment)

            access_role = self.check_access_role(assignment_list)
            if not access_role:
                return False

        today = datetime.today().strftime('%m/%d/%Y %H:%M:%S')

        return request.render(
            "openeducat_assignment_enterprise."
            "portal_student_submit_assignment_data",
            {
                'student_ids': student,
                'assignment_id': assignment_id,
                'submit_assignment_ids': assignment_list,
                'submit_date': today,
                'page_name': 'submit_assignment_form',
            })

    @http.route(['/assignment/submited/<int:assign_id>',
                 '/assignment/submited/<int:student_id>/<int:assign_id>',
                 '/assignment/submited/<int:assign_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_submit_assignment_create(self, assign_id, **kw):
        date = dateutil.parser.parse(kw['Date']).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)

        vals = {
            'student_id': int(kw['stud_id']),
            'submission_date': date,
            'assignment_id': int(kw.get('assignment_id')),
            'description': kw['Description'],
            'note': kw['Note'],
        }
        assignment_id = request.env[
            'op.assignment.sub.line'].sudo().create(vals)
        assignment_id.act_submit()

        if 'attachments' in request.params:
            attached_files = request.httprequest.files.getlist('attachments')
            for attachment in attached_files:
                attached_file = attachment.read()
                request.env['ir.attachment'].sudo().create({
                    'name': attachment.filename,
                    'res_model': 'op.assignment.sub.line',
                    'res_id': assignment_id,
                    'type': 'binary',
                    # 'name': attachment.filename,
                    'datas': base64.encodebytes(attached_file),
                })

        return request.redirect('/submited/assignment/list/%s' % assign_id)

    def _prepare_portal_layout_values(self):

        values = super(SubmitAssignment, self). \
            _prepare_portal_layout_values()
        user = request.env.user
        submission_count = request.env['op.assignment.sub.line'].sudo().search_count(
            [('user_id', '=', user.id)])
        values['submission_count'] = submission_count

        today = datetime.today()
        assignment_count = request.env['op.assignment'].sudo().search_count(
            [('allocation_ids.partner_id', '=', user.partner_id.id),
             ('state', '=', 'publish'),
             ('issued_date', '<=', today)])

        values['assignment_count'] = assignment_count
        return values

    def get_search_domain_submitted_assignment(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', ('assignment_id', 'ilike', srch),
                    ('state', 'ilike', srch), ('submission_date', 'ilike', srch)]

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

        val = super(SubmitAssignment, self). \
            _parent_prepare_portal_layout_values(student_id)
        student = request.env['op.student'].sudo().search(
            [('id', '=', student_id)])
        submission_count = request.env['op.assignment.sub.line']. \
            sudo().search_count([('user_id', '=', student.user_id.id)])
        val['submission_count'] = submission_count

        today = datetime.today()
        assignment_count = request.env['op.assignment'].sudo().search_count(
            [('allocation_ids.partner_id', '=', student.partner_id.id),
             ('state', '=', 'publish'),
             ('issued_date', '<=', today)])
        val['assignment_count'] = assignment_count
        return val

    @http.route(['/submited/assignment/list/<int:asgnmt_id>',
                 '/submited/assignment/list/<int:student_id>/<int:asgnmt_id>',
                 '/submited/assignment/list/<int:asgnmt_id>/page/<int:page>',
                 '/submited/assignment/list/<int:student_id>'
                 '/<int:asgnmt_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_submit_assignment_list(self, asgnmt_id, student_id=None, date_begin=None,
                                      date_end=None, page=0, search='', ppg=False,
                                      sortby=None, filterby=None, search_in='content',
                                      groupby='assignment_id', **post):
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

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'state submit': {'label': _('Submitted'),
                             'domain': [('state', '=', 'submit')]},
            'state reject': {'label': _('Rejected'),
                             'domain': [('state', '=', 'reject')]},
            'state change': {'label': _('Change Required'),
                             'domain': [('state', '=', 'change')]},
            'state accept': {'label': _('Accepted'),
                             'domain': [('state', '=', 'accept')]},
        }
        searchbar_inputs = {
            'content': {'input': 'content',
                        'label': Markup(_('Search <span class="nolabel"> '
                                          '(in Assignment)</span>'))},
            'submission_date': {'input': 'Submission Date',
                                'label': _('Search in Submission Date')},
            'state': {'input': 'State', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'assignment_id': {'input': 'assignment_id', 'label': _('Assignment')},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'content'):
                search_domain = expression.OR(
                    [search_domain, [('assignment_id', 'ilike', search)]])
            if search_in in ('all', 'submission_date'):
                search_domain = expression.OR([search_domain,
                                               [('submission_date', 'ilike', search)]])
            if search_in in ('all', 'state'):
                search_domain = expression.OR([search_domain,
                                               [('state', 'ilike', search)]])
            domain += search_domain

        domain += self.get_search_domain_submitted_assignment(search, attrib_values)

        searchbar_sortings = {
            'submission_date': {'label': _('SubmissionDate'),
                                'order': 'submission_date'},
            'assignment_id': {'label': _('Assignment '),
                              'order': 'assignment_id'},
            'state': {'label': _('State'), 'order': 'state'},
        }

        if not sortby:
            sortby = 'state'
        order = searchbar_sortings[sortby]['order']

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        if student_id:
            keep = QueryURL('/submited/assignment/list/%s' %
                            student_id + '/%s' % asgnmt_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))

            domain += [('student_id', '=', student_id),
                       ('assignment_id', '=', asgnmt_id)]
            total = request.env['op.assignment.sub.line'].sudo().search_count(domain)
            pager = portal_pager(
                url="/submited/assignment/list/%s" % student_id + "/%s" % asgnmt_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/submited/assignment/list/%s' % asgnmt_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))

            user = request.env.user
            domain += [('user_id', '=', user.id), ('assignment_id', '=', asgnmt_id)]
            total = request.env['op.assignment.sub.line'].sudo().search_count(domain)
            pager = portal_pager(
                url="/submited/assignment/list/%s" % asgnmt_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )

        if groupby == 'assignment_id':
            order = "assignment_id, %s" % order

        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')

            assignment_id = request.env[
                'op.assignment.sub.line'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        else:
            assignment_id = request.env[
                'op.assignment.sub.line'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        if groupby == 'assignment_id':
            grouped_tasks = [
                request.env['op.assignment.sub.line'].sudo().concat(*g)
                for k, g in groupbyelem(assignment_id, itemgetter('assignment_id'))]
        else:
            grouped_tasks = [assignment_id]

        assin_id = request.env['op.assignment'].sudo().search([('id', '=', asgnmt_id)])

        total_attempt = request.env['op.assignment.sub.line'].sudo(). \
            search_count([('student_id.user_id', '=', request.env.uid),
                          ('assignment_id', '=', asgnmt_id),
                          ('ignore_attempt', 'not in', [i.id for i in assignment_id])])

        allow_attempt = request.env['student.additional.attempt'].sudo(). \
            search([('student_id.user_id', '=', request.env.uid),
                    ('assignment_id', '=', asgnmt_id)])

        extra_attempts = 0
        for rec in allow_attempt:
            extra_attempts += rec.allowed_attempt
        additional_attempt = extra_attempts + assin_id.max_attempt

        if student_id:
            val.update({
                'date': date_begin,
                'submission_ids': assignment_id,
                'assin_id': assin_id,
                'id': asgnmt_id,
                'page_name': 'submission_list',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/submited/assignment/list/%s' %
                               student_id + '/%s' % asgnmt_id,
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
                "openeducat_assignment_enterprise.portal_submited_assignment_list",
                val)

        else:
            values.update({
                'date': date_begin,
                'submission_ids': assignment_id,
                'additional_attempt': additional_attempt,
                'allow_attempt': allow_attempt,
                'extra_attempts': extra_attempts,
                'total_attempt': total_attempt,
                'assin_id': assin_id,
                'id': asgnmt_id,
                'page_name': 'submission_list',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/submited/assignment/list/%s' % asgnmt_id,
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
                "openeducat_assignment_enterprise.portal_submited_assignment_list",
                values)

    def check_submission_access(self, submission_id=None):
        submission = request.env['op.assignment.sub.line'].sudo().search(
            [('id', '=', submission_id)])

        user = request.env.user
        user_list = []
        count = 0
        for rec in submission.student_id:
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

    @http.route(['/assignment/data/<int:assignment_id>',
                 '/assignment/data/<int:student_id>/<int:assignment_id>'],
                type='http', auth="user", website=True)
    def portal_submited_assignment_data(self, student_id=None,
                                        assignment_id=None):

        submission_instance = request.env[
            'op.assignment.sub.line'].sudo().search(
            [('id', '=', assignment_id)])
        attachment_instance = submission_instance.attachment_ids
        access_role = self.check_submission_access(submission_instance.id)
        if access_role is False:
            return Response("[Bad Request]", status=404)

        return request.render(
            "openeducat_assignment_enterprise.assignment_data", {
                'assignment_ids': submission_instance,
                'attachment_ids': attachment_instance,
                'student': student_id,
                'page_name': 'submission_info',
            })

    @http.route(['/assignment/submission/download/<int:attachment_id>'],
                type='http', auth='user', website=True)
    def download_submission_attachment(self, attachment_id):

        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"]
        )
        if attachment:
            attachment = attachment[0]
        res_id = attachment['res_id']
        submission_id = request.env['op.assignment.sub.line'].sudo().search(
            [('id', '=', res_id)])
        access_role = self.check_submission_access(submission_id.id)
        if access_role is False:
            return Response("[Bad Request]", status=404)

        if submission_id:
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

    def check_assignment_access(self, assignment_id=None):

        assignment = request.env['op.assignment'].sudo().search(
            [('id', '=', assignment_id)])

        user = request.env.user
        user_list = []
        count = 0
        for rec in assignment.allocation_ids:
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

    @http.route(['/assignment/details/<int:assignment_id>',
                 '/assignment/details/<int:student_id>/<int:assignment_id>'],
                type='http', auth='user', website=True)
    def assignment_details(self, student_id=None, assignment_id=None):

        assignment = request.env['op.assignment'].sudo().search(
            [('id', '=', assignment_id)])

        access_role = self.check_assignment_access(assignment.id)
        if access_role is False:
            return Response("[Bad Request]", status=404)

        return request.render(
            "openeducat_assignment_enterprise.assignment_details",
            {'assignment': assignment,
             'student': student_id,
             'page_name': 'assignment_info'})

    @http.route(['/assignment/attachment/download/<int:attachment_id>'],
                type='http', auth='user', website=True)
    def download_assignment_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"])
        if attachment:
            attachment = attachment[0]
        res_id = attachment['res_id']
        assignment_id = request.env['op.assignment'].sudo().search(
            [('id', '=', res_id)])

        access_role = self.check_assignment_access(assignment_id.id)
        if access_role is False:
            return Response("[Bad Request]", status=404)

        if assignment_id:
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

    def get_search_domain_assignment(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', '|', '|', ('name', 'ilike', srch),
                    ('course_id', 'ilike', srch), ('assignment_type_id', 'ilike', srch),
                    ('state', 'ilike', srch), ('issued_date', 'ilike', srch),
                    ('submission_date', 'ilike', srch)]

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

    @http.route(['/student/assignment/details',
                 '/student/assignment/details/<int:student_id>',
                 '/student/assignment/details/page/<int:page>',
                 '/student/assignment/details/<int:student_id>/page/<int:page>',
                 ],
                type='http', auth='user', website=True)
    def student_assignment_details(self, student_id=None, date_begin=None,
                                   date_end=None, page=1, search='', ppg=False,
                                   sortby=None, filterby=None, search_in='content',
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
            'course_id': {'label': _('Course'), 'order': 'course_id'},
            'batch_id': {'label': _('Batch'), 'order': 'batch_id'},
            'marks': {'Payable At': _('Marks'), 'order': 'marks desc'},
            'submission_date': {'label': _('SubmissionDate'),
                                'order': 'submission_date '},
            'issued_date': {'label': _('IssuedDate'), 'order': 'issued_date'},
            'state': {'label': _('State'), 'order': 'state'},
        }
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'state': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'state publish': {'label': _('Publish'),
                              'domain': [('state', '=', 'publish')]},
            'state cancel': {'label': _('Cancel'),
                             'domain': [('state', '=', 'cancel')]},
            'state finish': {'label': _('Finish'),
                             'domain': [('state', '=', 'finish')]},
        }
        searchbar_inputs = {
            'content': {'input': 'content',
                        'label': Markup(_('Search <span class="nolabel"> '
                                          '(in Assignment)</span>'))},
            'course_id': {'input': 'Course', 'label': _('Search in Course')},
            'assignment_type_id': {'input': 'Assignment Type',
                                   'label': _('Search in Assignment Type')},
            'issued_date': {'input': 'Issued Date',
                            'label': _('Search in Issued Date')},
            'submission_date': {'input': 'Submission Date',
                                'label': _('Search in Submission Date')},
            'state': {'input': 'State', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'course_id': {'input': 'course_id', 'label': _('Course')},
        }

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'content'):
                search_domain = expression.OR(
                    [search_domain, [('name', 'ilike', search)]])
            if search_in in ('all', 'course_id'):
                search_domain = expression.OR(
                    [search_domain, [('course_id', 'ilike', search)]])
            if search_in in ('all', 'assignment_type_id'):
                search_domain = expression.OR(
                    [search_domain, [('assignment_type_id', 'ilike', search)]])
            if search_in in ('all', 'issued_date'):
                search_domain = expression.OR(
                    [search_domain, [('issued_date', 'ilike', search)]])
            if search_in in ('all', 'submission_date'):
                search_domain = expression.OR(
                    [search_domain, [('submission_date', 'ilike', search)]])
            if search_in in ('all', 'state'):
                search_domain = expression.OR(
                    [search_domain, [('state', 'ilike', search)]])
            domain += search_domain

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        domain += self.get_search_domain_assignment(search, attrib_values)
        if student_id:
            keep = QueryURL('/student/assignment/details/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))
            partner = request.env['op.student'].sudo().search([('id', '=', student_id)])
            today = datetime.today()
            domain += [('allocation_ids.partner_id', '=', partner.partner_id.id),
                       ('state', '=', 'publish'),
                       ('issued_date', '<=', today)]
            total = request.env['op.assignment'].sudo().search_count(domain)

            pager = portal_pager(
                url="/student/assignment/details/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/student/assignment/details',
                            search=search, attrib=attrib_list,
                            order=post.get('order'))

            partner = request.env.user.partner_id
            today = datetime.today()
            domain += [('allocation_ids.partner_id', '=', partner.id),
                       ('state', '=', 'publish'),
                       ('issued_date', '<=', today)]
            total = request.env['op.assignment'].sudo().search_count(domain)

            pager = portal_pager(
                url="/student/assignment/details",
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
            student_data = request.env['op.assignment'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
        else:
            student_data = request.env[
                'op.assignment'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        if groupby == 'course_id':
            grouped_tasks = [
                request.env['op.assignment'].sudo().concat(*g)
                for k, g in groupbyelem(student_data, itemgetter('course_id'))]
        else:
            grouped_tasks = [student_data]

        if student_id:
            val.update({
                'date': date_begin,
                'assignment_id': student_data,
                'page_name': 'Student_assignment',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/student/assignment/details/%s' % student_id,
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
                "openeducat_assignment_enterprise.openeducat_student_assignments",
                val)

        else:
            values.update({
                'date': date_begin,
                'assignment_id': student_data,
                'page_name': 'Student_assignment',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/student/assignment/details',
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
                "openeducat_assignment_enterprise.openeducat_student_assignments",
                values)
