# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


from collections import OrderedDict
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


class MeetingPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(MeetingPortal, self)._prepare_portal_layout_values()
        student = request.env['op.student'].sudo().search(
            [('user_id', '=', request.env.uid)])
        meeting_count = request.env['calendar.event'].sudo().search_count(
            [('partner_ids', '=', student.partner_id.id)])
        values['meeting_count'] = meeting_count
        return values

    def get_search_domain_meeting(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', '|', ('name', 'ilike', srch),
                    ('start', 'ilike', srch), ('stop', 'ilike', srch),
                    ('location', 'ilike', srch), ('duration', 'ilike', srch)]
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

        val = super(MeetingPortal, self). \
            _parent_prepare_portal_layout_values(student_id)
        student = request.env['op.student'].sudo().search(
            [('id', '=', student_id)])
        meeting_count = request.env['calendar.event'].sudo().search_count(
            [('partner_ids', '=', student.partner_id.id)])
        val['meeting_count'] = meeting_count
        return val

    @http.route(['/meeting/information/',
                 '/meeting/information/<int:student_id>',
                 '/meeting/information/page/<int:page>',
                 '/meeting/information/<int:student_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_meeting_list(self, date_begin=None, student_id=None, date_end=None,
                            page=1, search=None, ppg=False, sortby=None, filterby=None,
                            search_in='content', groupby='name', **post):
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
            'meeting_id': {'label': _('Meeting'), 'order': 'meeting_id'},
            'start': {'label': _('Start Date'), 'order': 'start'},
        }
        if not sortby:
            sortby = 'meeting_id'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content',
                        'label': Markup(_('Search <span class="nolabel"> '
                                          '(in Subject)</span>'))},
            'start': {'input': 'Start Date', 'label': _('Search in StartDate')},
            'stop': {'input': 'End Date', 'label': _('Search in EndDate')},
            'location': {'input': 'Location', 'label': _('Search in Location')},
            'duration': {'input': 'Duration', 'label': _('Search in Duration')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'name': {'input': 'name', 'label': _('Subject')},
        }
        meetings = request.env['calendar.event'].sudo().search([])
        for meeting in meetings:
            searchbar_filters.update({
                str(meeting.name): {'label': meeting.name,
                                    'domain': [('name', '=', meeting.name)]}
            })
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'content'):
                search_domain = expression.OR(
                    [search_domain, [('name', 'ilike', search)]])
            if search_in in ('all', 'start'):
                search_domain = expression.OR([search_domain,
                                               [('start', 'ilike', search)]])
            if search_in in ('all', 'stop'):
                search_domain = expression.OR([search_domain,
                                               [('stop', 'ilike', search)]])
            if search_in in ('all', 'location'):
                search_domain = expression.OR([search_domain,
                                               [('location', 'ilike', search)]])
            if search_in in ('all', 'duration'):
                search_domain = expression.OR([search_domain,
                                               [('duration', 'ilike', search)]])
            domain += search_domain

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        domain += self.get_search_domain_meeting(search, attrib_values)
        if student_id:

            keep = QueryURL('/meeting/information/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))

            total = request.env['calendar.event'].sudo().search_count(domain)

            pager = portal_pager(
                url="/meeting/information/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_id': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/meeting/information/', search=search,
                            attrib=attrib_list,
                            order=post.get('order'))

            total = request.env['op.meeting'].sudo().search_count(domain)

            pager = portal_pager(
                url="/meeting/information/",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_id': search_in},
                total=total,
                page=page,
                step=ppg
            )
        if groupby == 'name':
            order = "name, %s" % order

        meeting_id = request.env["op.meeting"].sudo().search(
            domain, order=order, limit=ppg, offset=pager['offset'])

        if groupby == 'name':
            grouped_tasks = [
                request.env['op.meeting'].sudo().concat(*g)
                for k, g in groupbyelem(meeting_id, itemgetter('name'))]
        else:
            grouped_tasks = [meeting_id]

        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')

            val.update({
                'date': date_begin,
                'meeting_ids': meeting_id,
                'page_name': 'Meetings_detail',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/meeting/information/%s' % student_id,
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
                "openeducat_meeting_enterprise.openeducat_meeting_portal",
                val)
        else:
            values.update({
                'date': date_begin,
                'meeting_ids': meeting_id,
                'page_name': 'Meetings_detail',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/meeting/information/',
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
                "openeducat_meeting_enterprise.openeducat_meeting_portal",
                values)

    @http.route(['/meeting/information/data/<int:meeting_id>',
                 '/meeting/information/data/<int:student_id>/<int:meeting_id>'],
                type='http', auth="user", website=True)
    def portal_meeting_form(self, meeting_id, student_id=None, **kw):

        meeting_all_id = request.env['op.meeting'].sudo().search(
            [('id', '=', meeting_id)])

        return request.render(
            "openeducat_meeting_enterprise.openeducat_meeting_portal_data",
            {'meeting': meeting_all_id,
             'student': student_id,
             'page_name': 'meeting', })

    @http.route('/get-meeting/data', type='json', auth='user', website=True)
    def get_meeting_data_portal(self, stud_id=None, current_timezone=None):
        data = []
        if stud_id:
            student = request.env['op.student'].sudo().search(
                [('id', '=', int(stud_id))])
        else:
            student = request.env['op.student'].sudo().search(
                [('user_id', '=', request.env.uid)])

        meeting_id = request.env["calendar.event"].sudo().search(
            [('partner_ids', '=', student.partner_id.id)])
        user_tz = request.env.user.tz or current_timezone or 'UTC'
        for meeting in meeting_id:
            data.append({
                'title': meeting.name,
                'start': meeting.start.astimezone(timezone(user_tz)),
                'end': meeting.stop.astimezone(timezone(user_tz)),
                'meeting_url': meeting.meeting_url,
                'duration_time': meeting.duration,
                'url': '/meeting/information/data/' + str(meeting.id),
            })
        return data
