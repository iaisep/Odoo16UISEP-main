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

from markupsafe import Markup

from odoo import _, http
from odoo.http import Response, request
from odoo.osv import expression

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

PPG = 9


class PortalNoticeBoard(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(PortalNoticeBoard, self)._prepare_portal_layout_values()

        student = request.env['op.student'].sudo(). \
            search([('user_id', '=', request.env.user.id)])

        notice_count = request.env['op.notice'].sudo().search_count(
            [('group_id.student_ids', 'in', student.id),
             ('state', '=', 'publish')])
        notice_count += request.env['op.circular'].sudo().search_count(
            [('group_id.student_ids', 'in', student.id),
             ('state', '=', 'publish')])

        values['notice_count'] = notice_count
        return values

    def _parent_prepare_portal_layout_values(self, student_id=None):
        val = super(PortalNoticeBoard, self)._parent_prepare_portal_layout_values(
            student_id)

        parent = request.env['op.parent'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        parent_id = parent.id

        notice_count = request.env['op.notice'].sudo().search_count(
            ['|', ('group_id.parent_ids', 'in', parent_id),
             ('group_id.student_ids', 'in', student_id),
             ('state', '=', 'publish')])
        notice_count += request.env['op.circular'].sudo().search_count(
            ['|', ('group_id.parent_ids', 'in', parent_id),
             ('group_id.student_ids', 'in', student_id),
             ('state', '=', 'publish')])

        val['notice_count'] = notice_count
        return val

    def get_search_domain_studnet_notice_queue(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                srch = srch.lower()
                domain += [
                    '|', ('name', 'ilike', srch),
                    ('created_by.name', 'ilike', srch)]

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

    def check_notice_access(self, notice_id=None):
        notice = request.env['op.notice'].sudo().search(
            [('id', '=', notice_id)])

        user = request.env.user
        user_list = []
        count = 0
        if notice.group_id.student_ids:
            for rec in notice.group_id.student_ids:
                if rec.user_id:
                    user_list.append(rec.user_id)
        if notice.group_id.parent_ids:
            for rec in notice.group_id.parent_ids:
                if rec.user_id:
                    user_list.append(rec.user_id)
        if user.partner_id.is_parent:
            parent_id = request.env['op.parent'].sudo().search(
                [('name', '=', user.partner_id.id)])
            for student_id in parent_id.student_ids:
                if student_id.user_id in user_list or parent_id.user_id in user_list:
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

    def check_circular_access(self, circular_id=None):
        circular = request.env['op.circular'].sudo().search(
            [('id', '=', circular_id)])

        user = request.env.user
        user_list = []
        count = 0
        if circular.group_id.student_ids:
            for rec in circular.group_id.student_ids:
                if rec.user_id:
                    user_list.append(rec.user_id)
        if circular.group_id.parent_ids:
            for rec in circular.group_id.parent_ids:
                if rec.user_id:
                    user_list.append(rec.user_id)
        if user.partner_id.is_parent:
            parent_id = request.env['op.parent'].sudo().search(
                [('name', '=', user.partner_id.id)])
            for student_id in parent_id.student_ids:
                if student_id.user_id in user_list or parent_id.user_id in user_list:
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

    @http.route(['/my/notice_board/notice/',
                 '/my/notice_board/notice/<int:student_id>',
                 '/my/notice_board/notice/page/<int:page>',
                 '/my/notice_board/notice/<int:student_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_student_notice_board_notice(self, student_id=None, sortby=None,
                                           search='', page=0, ppg=False,
                                           start_date=None, end_date=None,
                                           search_in='all', **post):

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
            'high_priority': {'label': _('Priority'), 'order': 'high_priority'},
            'date': {'label': _('Date'), 'order': 'start_date'},
            'name': {'label': _('Title'), 'order': 'name'}}

        if not sortby:
            sortby = 'high_priority'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        searchbar_inputs = {
            'name': {'input': 'name',
                     'label': Markup(_('Search <span class="nolabel"> '
                                       '(Title)</span>'))},
            'created_by': {'input': 'created_by',
                           'label': _('Search in Sender')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        domain = self.get_search_domain_studnet_notice_queue(search, attrib_values)

        if student_id:
            keep = QueryURL('/my/notice_board/notice/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))
            parent = request.env['op.parent'].sudo().search(
                [('user_id', '=', request.env.user.id)])
            parent_id = parent.id
            domain += ['|', ('group_id.parent_ids', 'in', parent_id),
                       ('group_id.student_ids', 'in', student_id),
                       ('state', '=', 'publish')]
            total = request.env['op.notice'].sudo().search_count(domain)

            pager = portal_pager(
                url="/my/notice_board/notice/%s" % student_id,
                url_args={'start_date': start_date, 'end_date': end_date,
                          'sortby': sortby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/my/notice_board/notice/',
                            search=search, search_in=search_in, attrib=attrib_list,
                            order=post.get('order'))
            student = request.env['op.student'].sudo(). \
                search([('user_id', '=', request.env.user.id)])

            domain = [('group_id.student_ids', 'in', student.id),
                      ('state', '=', 'publish')]
            total = request.env['op.notice'].sudo().search_count(domain)

            pager = portal_pager(
                url="/my/notice_board/notice/",
                url_args={'start_date': start_date, 'end_date': end_date,
                          'sortby': sortby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'name'):
                search_domain = expression.OR(
                    [search_domain, [('name', 'ilike', search)]])
            if search_in in ('all', 'created_by'):
                search_domain = expression.OR(
                    [search_domain, [('created_by.name', 'ilike', search)]])
            if search_in in ('all', 'start_date'):
                search_domain = expression.OR(
                    [search_domain, [('start_date', 'ilike', search)]])
            domain += search_domain

        if student_id:
            notice_list = request.env['op.notice'].sudo().search(
                domain, limit=ppg, order=order, offset=pager['offset'])

            attributes = request.env[
                'op.notice'].browse(attributes_ids)
            val.update({'notice_ids': notice_list,
                        'page_name': 'notice_board',
                        'users_id': request.env.user,
                        'keep': keep,
                        'student': student_id,
                        'pager': pager,
                        'default_url': '/my/notice_board/notice/%s' % student_id,
                        'attrib_values': attrib_values,
                        'attrib_set': attrib_set,
                        'searchbar_inputs': searchbar_inputs,
                        'search_in': search_in,
                        'attributes': attributes,
                        'searchbar_filters': OrderedDict(
                            sorted(searchbar_filters.items())),
                        'searchbar_sortings': searchbar_sortings,
                        'sortby': sortby,
                        })
            return request.render('openeducat_notice_board_enterprise.'
                                  'student_notice_board_notice_portal',
                                  val)

        else:
            student = request.env['op.student'].sudo().search(
                [('user_id', '=', request.env.user.id)])
            student_id = student.id

            notice_list = request.env['op.notice'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
            attributes = request.env[
                'op.notice'].browse(attributes_ids)

            values.update({'notice_ids': notice_list,
                           'page_name': 'notice_board',
                           'users_id': request.env.user,
                           'keep': keep,
                           'student': student_id,
                           'pager': pager,
                           'default_url': '/my/notice_board/notice/',
                           'attrib_values': attrib_values,
                           'attrib_set': attrib_set,
                           'searchbar_inputs': searchbar_inputs,
                           'search_in': search_in,
                           'attributes': attributes,
                           'searchbar_filters': OrderedDict(
                               sorted(searchbar_filters.items())),
                           'searchbar_sortings': searchbar_sortings,
                           'sortby': sortby,
                           })
            return request.render('openeducat_notice_board_enterprise.'
                                  'student_notice_board_notice_portal',
                                  values)

    @http.route(['/my/notice_board/circular/',
                 '/my/notice_board/circular/<int:student_id>',
                 '/my/notice_board/circular/page/<int:page>',
                 '/my/notice_board/circular/<int:student_id>/page/<int:page>'
                 ],
                type='http', auth="user", website=True)
    def portal_student_notice_board_circular(self, student_id=None, sortby=None,
                                             search='', start_date=None,
                                             end_date=None, page=0, ppg=False,
                                             search_in='all',
                                             **post):
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
            'date': {'label': _('Date'), 'order': 'start_date'},
            'name': {'label': _('Title'), 'order': 'name'}}

        if not sortby:
            sortby = 'date'

        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        searchbar_inputs = {
            'name': {'input': 'name',
                     'label': Markup(_('Search <span class="nolabel"> '
                                       '(Title)</span>'))},
            'created_by': {'input': 'created_by',
                           'label': _('Search in Sender')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        domain = self.get_search_domain_studnet_notice_queue(search, attrib_values)

        if student_id:
            keep = QueryURL('/my/notice_board/circular/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))
            parent = request.env['op.parent'].sudo().search(
                [('user_id', '=', request.env.user.id)])
            parent_id = parent.id
            domain += ['|', ('group_id.parent_ids', 'in', parent_id),
                       ('group_id.student_ids', 'in', student_id),
                       ('state', '=', 'publish')]
            total = request.env['op.circular'].sudo().search_count(domain)

            pager = portal_pager(
                url="/my/notice_board/circular/%s" % student_id,
                url_args={'start_date': start_date, 'end_date': end_date,
                          'sortby': sortby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/my/notice_board/circular/',
                            search=search, attrib=attrib_list, order=post.get('order'))
            student = request.env['op.student'].sudo(). \
                search([('user_id', '=', request.env.user.id)])

            domain += [('group_id.student_ids', 'in', student.id),
                       ('state', '=', 'publish')]
            total = request.env['op.circular'].sudo().search_count(domain)

            pager = portal_pager(
                url="/my/notice_board/circular/",
                url_args={'start_date': start_date, 'end_date': end_date,
                          'sortby': sortby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'name'):
                search_domain = expression.OR(
                    [search_domain, [('name', 'ilike', search)]])
            if search_in in ('all', 'created_by.name'):
                search_domain = expression.OR(
                    [search_domain, [('created_by.name', 'ilike', search)]])
            if search_in in ('all', 'start_date'):
                search_domain = expression.OR(
                    [search_domain, [('start_date', 'ilike', search)]])
            domain += search_domain

        if student_id:
            circular_list = request.env['op.circular'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

            attributes = request.env[
                'op.circular'].browse(attributes_ids)
            val.update({
                'circular_ids': circular_list,
                'page_name': 'circular_board',
                'keep': keep,
                'student': student_id,
                'pager': pager,
                'default_url': '/my/notice_board/circular/%s' % student_id,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'attributes': attributes,
                'searchbar_filters': OrderedDict(
                    sorted(searchbar_filters.items())),
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
            })
            return request.render('openeducat_notice_board_enterprise.'
                                  'student_notice_board_notice_circular_portal',
                                  val)

        else:
            student = request.env['op.student'].sudo().search(
                [('user_id', '=', request.env.user.id)])
            student_id = student.id
            circular_list = request.env['op.circular'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

            attributes = request.env[
                'op.circular'].browse(attributes_ids)

            values.update({
                'circular_ids': circular_list,
                'page_name': 'circular_board',
                'users_id': request.env.user,
                'keep': keep,
                'student': student_id,
                'pager': pager,
                'default_url': '/my/notice_board/circular/',
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'attributes': attributes,
                'searchbar_filters': OrderedDict(
                    sorted(searchbar_filters.items())),
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
            })
            return request.render('openeducat_notice_board_enterprise.'
                                  'student_notice_board_notice_circular_portal',
                                  values)

    @http.route(['/notice_board/notice/<int:notice_id>',
                 '/notice_board/notice/<int:student_id>/<int:notice_id>'],
                type='http', auth='user', website=True)
    def notice_details(self, student_id=None, notice_id=None):

        notice = request.env['op.notice'].sudo().search(
            [('id', '=', notice_id)])

        attchments = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'op.notice'), ('res_id', '=', notice_id)])
        access_role = self.check_notice_access(notice.id)
        if access_role is False:
            return Response("[Bad Request]", status=404)

        return request.render(
            "openeducat_notice_board_enterprise.notice_details",
            {'notice': notice,
             'student': student_id,
             'attachment_ids': attchments,
             'page_name': 'notice_info'})

    @http.route(['/notice_board/circular/<int:circular_id>',
                 '/notice_board/circular/<int:student_id>/<int:circular_id>'],
                type='http', auth='user', website=True)
    def circular_details(self, student_id=None, circular_id=None):

        circular = request.env['op.circular'].sudo().search(
            [('id', '=', circular_id)])

        attchments = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'op.circular'), ('res_id', '=', circular_id)])

        access_role = self.check_circular_access(circular.id)
        if access_role is False:
            return Response("[Bad Request]", status=404)

        return request.render(
            "openeducat_notice_board_enterprise.circular_details",
            {'circular': circular,
             'student': student_id,
             'attachment_ids': attchments,
             'page_name': 'circular_info'})

    @http.route(['/notice/document/attachment/download/'
                 '<int:notice_id>/<int:attachment_id>'],
                type='http', auth='user', website=True)
    def download_notice_document_attachment(self, attachment_id=None, notice_id=None):
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"])
        if attachment:
            attachment = attachment[0]

        if notice_id:
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

    @http.route(['/circular/document/attachment/download/'
                 '<int:circular_id>/<int:attachment_id>'],
                type='http', auth='user', website=True)
    def download_circular_document_attachment(self,
                                              attachment_id=None, circular_id=None):
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"])
        if attachment:
            attachment = attachment[0]

        if circular_id:
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
