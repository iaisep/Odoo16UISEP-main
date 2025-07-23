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
from odoo.http import Response, request
from odoo.osv import expression
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

PPG = 5  # record per page


class OnlineMeetingPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):

        values = super(OnlineMeetingPortal, self)._prepare_portal_layout_values()
        user = request.env.user

        online_meeting_count = request.env['calendar.event'].sudo().search_count(
            [('partner_ids', '=', user.partner_id.id),
             ('online_meeting', '=', True)])
        values['online_meeting_count'] = online_meeting_count

        return values

    def _parent_prepare_portal_layout_values(self, student_id=None):

        val = super(OnlineMeetingPortal, self). \
            _parent_prepare_portal_layout_values(student_id)
        student = request.env['op.student'].sudo().search([('id', '=', student_id)])
        online_meeting_count = request.env['calendar.event'].sudo().search_count(
            [('partner_ids', '=', student.partner_id.id),
             ('online_meeting', '=', True)])
        val['online_meeting_count'] = online_meeting_count
        return val

    def get_search_domain_online_meeting(self, search, attrib_values):
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

    def check_online_meeting_access(self, meeting_id=None):

        meeting_id = request.env['calendar.event'].sudo().search(
            [('id', '=', meeting_id), ('online_meeting', '=', True)])
        user = request.env.user
        user_list = []
        count = 0
        for rec in meeting_id:
            if rec.partner_ids:
                for partner in rec.partner_ids:
                    user_list.append(partner.id)
        if user.partner_id.is_parent:
            parent_id = request.env['op.parent'].sudo().search(
                [('name', '=', user.partner_id.id)])
            for student_id in parent_id.student_ids:
                if student_id.partner_id.id in user_list:
                    count += 1
            if count > 0:
                return True
            else:
                return False
        else:
            if user.partner_id.id not in user_list:
                return False
            else:
                return True

    @http.route(['/online/meeting/',
                 '/online/meeting/<int:student_id>',
                 '/online/meeting/page/<int:page>',
                 '/online/meeting/<int:student_id>/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_online_meeting_list(self, student_id=None, date_begin=None,
                                   date_end=None, page=0, search='', ppg=False,
                                   sortby=None, filterby=None, search_in='content',
                                   groupby='name', **post):
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
            'start_date': {'label': _('Start Date'), 'order': 'start_date'},
        }
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        searchbar_inputs = {
            'content': {'input': 'content',
                        'label': Markup(_('Search <span class="nolabel">'
                                          ' (in Subject)</span>'))},
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
        domain = [('partner_ids', '=', user.partner_id.id),
                  ('online_meeting', '=', True)]

        meetings = request.env['calendar.event'].sudo().search(domain)
        for meeting in meetings:
            searchbar_filters.update({
                str(meeting.name): {'label': meeting.name,
                                    'domain': [('name', '=', meeting.name)]}
            })
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

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

        domain += self.get_search_domain_online_meeting(search, attrib_values)
        keep = QueryURL('/online/meeting/', search=search, attrib=attrib_list,
                        order=post.get('order'))

        total = request.env['calendar.event'].sudo().search_count(
            domain)
        if student_id:
            pager = portal_pager(
                url="/online/meeting/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            pager = portal_pager(
                url="/online/meeting/",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        if groupby == 'name':
            order = "name, %s" % order

        tasks = request.env['calendar.event'].sudo().search(
            domain, order=order, limit=ppg, offset=pager['offset'])

        if groupby == 'name':
            grouped_tasks = [
                request.env['calendar.event'].sudo().concat(*g)
                for k, g in groupbyelem(tasks, itemgetter('name'))]
        else:
            grouped_tasks = [tasks]

        online_meeting_id = request.env["calendar.event"].sudo().search(
            domain, order=order, limit=ppg, offset=pager['offset'])

        if user.partner_id.is_parent:
            parent_id = request.env['op.parent'].sudo().search(
                [('name', '=', user.partner_id.id)])
            student_list = [rec.id for rec in parent_id.student_ids]

            if student_id in student_list:
                student = request.env['op.student'].sudo().search(
                    [('id', '=', student_id)])
                online_meeting_id = request.env["calendar.event"].sudo().search(
                    [('partner_ids', '=', student.partner_id.id),
                     ('online_meeting', '=', True)])

        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')

            val.update({
                'date': date_begin,
                'meeting_ids': online_meeting_id,
                'page_name': 'online_meeting',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/online/meeting/%s' % student_id,
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
                "openeducat_online_tools_enterprise.openeducat_online_meeting_portal",
                val)

        else:
            values.update({
                'date': date_begin,
                'meeting_ids': online_meeting_id,
                'page_name': 'online_meeting',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/online/meeting/',
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
                "openeducat_online_tools_enterprise.openeducat_online_meeting_portal",
                values)

    @http.route(['/online/meeting/information/<int:meeting_id>',
                 '/online/meeting/information/<int:student_id>/<int:meeting_id>',
                 '/online/meeting/information/<string:meeting_id_str>',
                 '/online/meeting/information/<int:student_id>/<string:meeting_id_str>',
                 ],
                type='http', auth="user", website=True)
    def portal_online_meeting_form(self, student_id=None, meeting_id=None,
                                   meeting_id_str=None, **kw):

        user = request.env.user
        if meeting_id_str:
            temp = meeting_id_str.split('-')
            meeting_id = int(temp[0])

            online_meeting_id = request.env['calendar.event'].sudo().search(
                [('id', '=', meeting_id)])
            res = self.check_online_meeting_access(meeting_id)
            if res is False:
                return Response("[Bad Request]", status=404)

        else:

            online_meeting_id = request.env['calendar.event'].sudo().search(
                [('id', '=', meeting_id)])
            res = self.check_online_meeting_access(online_meeting_id.id)
            if res is False:
                return Response("[Bad Request]", status=404)

        attendee = []
        for record in online_meeting_id.attendee_ids:
            if user.partner_id.is_parent:
                parent_id = request.env['op.parent'].sudo().search(
                    [('name', '=', user.partner_id.id)])
                for rec in parent_id.student_ids:
                    if rec.partner_id.id == record.partner_id.id:
                        attendee.append({
                            'email': record.email,
                            'url': record.attendee_meeting_url,
                            'apw': record.apw
                        })
            if user.partner_id.id == record.partner_id.id:
                attendee.append({
                    'email': record.email,
                    'url': record.attendee_meeting_url,
                    'apw': record.apw
                })

        return request.render(
            "openeducat_online_tools_enterprise.openeducat_online_meeting_portal_data",
            {'meeting_id': online_meeting_id,
             'attendees': attendee,
             'student': student_id,
             'page_name': 'online_meeting_info',
             })

    @http.route('/get-online-meeting/data', type='json', auth='user', website=True)
    def get_online_meeting_data_portal(self, stud_id=None, current_timezone=None):
        data = []
        if stud_id:

            student = request.env['op.student'].sudo().search(
                [('id', '=', int(stud_id))])
        else:
            student = request.env['op.student'].sudo().search(
                [('user_id', '=', request.env.uid)])

        online_meeting_id = request.env["calendar.event"].sudo().search(
            [('partner_ids', '=', student.partner_id.id),
             ('online_meeting', '=', True)])
        user_tz = request.env.user.tz or current_timezone or 'UTC'
        for meeting in online_meeting_id:
            data.append({
                'title': meeting.name,
                'start': meeting.start.astimezone(timezone(user_tz)),
                'end': meeting.stop.astimezone(timezone(user_tz)),
                'meeting_url': meeting.meeting_url,
                'duration_time': meeting.duration,
                'url': '/online/meeting/information/' + str(meeting.id),
            })
        return data
