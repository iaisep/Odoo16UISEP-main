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

import logging
_logger = logging.getLogger(__name__)

class TimeTablePortalURl(CustomerPortal):

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
                'lesson': all_lession,
                'time_url_metting':session.time_url_metting,
                'time_url_recoding':session.time_url_recoding,
            })
        _logger.info("data: %s", data)
        return data   