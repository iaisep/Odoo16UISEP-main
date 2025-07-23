# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import base64
import calendar
import re
from collections import OrderedDict
from datetime import date, datetime

import werkzeug
from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from odoo import SUPERUSER_ID, _, fields, http, tools
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import content_disposition, request
from odoo.osv import expression
from odoo.tools import consteq

from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.openeducat_quiz.controllers.main import OpeneducatQuizRender
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

PPG = 12  # Products Per Page
PPR = 4  # Products Per Row


class OpeneducatQuizRenderInherit(OpeneducatQuizRender):

    def get_quiz_result_data(self, values):
        res = super(OpeneducatQuizRenderInherit, self).get_quiz_result_data(
            values)
        res['course_val'] = False
        res['material_val'] = False
        res['section_val'] = False
        return res

    @http.route('/lms/course/add', type='http', auth='user',
                methods=['POST'], website=True)
    def lms_course_create(self, *args, **kw):
        channel = request.env['op.course'].create(
            self._slide_channel_prepare_values(**kw))
        return werkzeug.utils.redirect("/course-detail/%s" % (slug(channel)))

    def _slide_channel_prepare_values(self, **kw):
        category_ids = []
        if kw.get('category_ids'):
            category_ids = [int(item) for item in kw['category_ids'].split(',')]

        return {
            'online_course': True,
            'state': 'open',
            'name': kw['name'],
            'code': kw['code'],
            'full_description': kw.get('short_description'),
            'navigation_policy': kw.get('navigation_policy', 'free_learn'),
            'user_id': request.env.user.id,
            'category_ids': [(6, 0, category_ids)],
        }

    @http.route(['/lms/category/search_read'], type='json', auth='user',
                methods=['POST'], website=True)
    def lms_category_search_read(self, fields, domain):
        can_create = request.env['op.course.category'].check_access_rights(
            'create', raise_exception=False)
        return {
            'read_results': request.env['op.course.category'].search_read(domain,
                                                                          fields),
            'can_create': can_create,
        }

    @http.route()
    def quiz_result(self, **kwargs):
        val = super(OpeneducatQuizRenderInherit, self).quiz_result(**kwargs)
        values = {}
        for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        result = request.env['op.quiz.result'].browse(int(values['ExamID']))
        if result.quiz_id.lms and values['CoueseExamID']:
            course = request.env['op.course'].browse(
                int(values['CoueseExamID']))
            material = request.env['op.material'].browse(
                int(values['MaterialID']))
            section = request.env['op.course.section'].browse(
                int(values['SectionID']))
            return request.redirect(
                '/course/%s/section/%s/material/%s/result/%s' % (
                    course.id, section.id, material.id, result.id))
        return val


class OpenEduCatLms(CustomerPortal):
    # --------------------------------------------------
    # MAIN / SEARCH
    # --------------------------------------------------

    @http.route('/get/material', type='json', auth="public",
                sitemap=False, website=True)
    def get_material(self, material_id, **kw):
        if material_id:
            material = request.env['op.material'].sudo().browse([
                int(material_id)])
            return {'embed_code': material.embed_code,
                    'webpage_content': material.webpage_content,
                    'name': material.name,
                    'material_type': material.material_type}

    @http.route(['/become-instructor'], type='http', auth="user",
                website=True)
    def register_faculty(self, **kwargs):
        faculty_group = request.env.ref('openeducat_lms.group_op_lms_user')
        faculty_ref = request.env['op.faculty']
        faculty = faculty_ref.sudo().search(
            [('user_id', '=', request.env.uid)])
        if not faculty:
            faculty = faculty_ref.sudo().create(
                {'partner_id': request.env.user.partner_id.id,
                 'last_name': kwargs.get('last_name', False),
                 'gender': kwargs.get('gender', False),
                 'birth_date': kwargs.get('birth_date', False),
                 'bio_data': kwargs.get('bio_data', False),
                 'designation': kwargs.get('designation', False)})
            faculty.sudo().user_id = request.env.user.id
            group_ids = faculty.user_id.groups_id.ids
            group_ids.append(faculty_group.id)
            faculty.user_id.sudo().groups_id = [[6, 0, list(set(group_ids))]]
        elif not faculty.user_id.has_group('openeducat_lms.group_op_lms_user'):
            group_ids = faculty.user_id.groups_id.ids
            group_ids.append(faculty_group.id)
            faculty.user_id.sudo().groups_id = [[6, 0, list(set(group_ids))]]
        return request.redirect('/courses')

    @http.route(['''/course/enroll/<model("op.course"):course>'''],
                type='http', auth="user", website=True)
    def enroll_course(self, course, **kwargs):
        course_ref = request.env['op.course.enrollment']
        enrollment = course_ref.sudo().search(
            [('user_id', '=', request.env.user.id),
             ('course_id', '=', course.id)])
        if not enrollment:
            course_ref.sudo().create({
                'user_id': request.env.user.id,
                'course_id': course.id,
                'enrollment_date': fields.Datetime.now(),
                'state': 'in_progress',
            })
        # student = student_ref.sudo().search(
        #     [('user_id', '=', request.env.uid)])
        # if not student:
        #     student = request.env['op.student'].sudo().create(
        #         {'name': request.env.user.name,
        #          'first_name': request.env.user.name,
        #          'partner_id': request.env.user.partner_id.id,
        #          'user_id': request.env.uid})
        return request.redirect('/course/%s' % slug(course))

    @http.route([
        '/courses',
        '/courses/page/<int:page>',
        '/courses/category/<model("op.course.category"):category>',
        '/courses/category/<model(\
        "op.course.category"):category>/page/<int:page>'
    ], type='http', auth="public", sitemap=False, website=True)
    def courses(self, search='', category=False, page=0, ppg=False,
                level=False, **post):
        if post.get('type') and post.get('type') not in ['free', 'paid']:
            post.update({
                'type': ''
            })
        keep = QueryURL("/courses", search=search, category=category, level=level,
                        type=post.get("type"))
        if category:
            category = request.env['op.course.category'].sudo().browse(int(category))
        if level:
            level = request.env['op.course.level'].sudo().browse(int(level))

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        domain = [('online_course', '=', True)]
        url = "/courses"
        if search:
            post["search"] = search
            for srch in search.split(" "):
                domain += [('name', 'ilike', srch)]
        if post.get('type'):
            domain += [('type', '=', post.get('type'))]
        if level:
            domain += [('level_id', '=', level.id)]
        if category:
            url = "/courses/category/%s" % slug(category)
            domain += [('category_ids', 'in', [category.id])]
        course_domain = domain + [
            ('visibility', 'in', ['public', 'logged_user']),
            ('state', '=', 'open')]
        course_ref = request.env['op.course']
        courses = course_ref.sudo().search(course_domain)
        invited_domain = domain + [
            ('invited_users_ids', 'in', [request.env.uid]),
            ('state', '=', 'open')]
        invited_courses = course_ref.sudo().search(invited_domain)
        total_count = len(courses) + len(invited_courses)
        pager = request.website.pager(
            url=url, total=total_count, page=page, step=ppg, scope=7,
            url_args=post)
        all_course_ids = [x.id for x in courses]
        all_course_ids += [x.id for x in invited_courses]
        all_courses = course_ref.sudo().search(
            [('id', 'in', all_course_ids)], limit=ppg,
            order='sequence asc', offset=pager['offset'])
        course_category_ref = request.env['op.course.category']
        levels = request.env['op.course.level'].sudo().search([])
        if category:
            categories = course_category_ref.sudo().search(
                [('parent_id', '=', category.id)])
        else:
            categories = course_category_ref.sudo().search(
                [('parent_id', '=', False)])
        values = {
            'search': search,
            'pager': pager,
            'search_count': total_count,
            'courses': all_courses,
            'category': category,
            'categories': categories,
            'levels': levels,
            'current_level': level,
            'current_type': post.get('type'),
            'keep': keep,
            'rows': 3,
            'user': request.env.user,
            'is_instructor': request.env.user.has_group(
                'openeducat_lms.group_op_lms_user')
        }
        return request.render("openeducat_lms.courses", values)

    def my_corse_details(self, enrollments):
        courses = []
        for en in enrollments:
            date_completed = False
            per = 0
            if en and en.course_id.training_material > 0:
                viewed_material = request.env[
                    'op.course.enrollment.material'].sudo().search_count(
                    [('completed', '=', True),
                     ('course_id', '=', en.course_id.id),
                     ('enrollment_id', '=', en.id)])
                per = viewed_material * 100 / en.course_id.training_material
            if en.completion_date:
                date_completed = (en.completion_date).strftime("%Y-%m-%d")
            courses.append({
                'course': en.course_id,
                'enrolled': en.state in [
                    'in_progress', 'done'] and True or False,
                'completed_percentage': per,
                'completion_date': date_completed})
        return {
            'courses': courses,
            'user': request.env.user,
            'is_public_user': request.env.user == request.website.user_id
        }

    @http.route(['/my-courses', '/my-courses/<int:student_id>'],
                type='http', auth="public", sitemap=False, website=True)
    def my_courses(self, student_id=None, *args, **post):
        # Show Courses To Logged in User
        search = post.get('search')
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [('course_id.name', 'ilike', srch)]

        if student_id:
            student = request.env['op.student'].sudo().search([('id', '=', student_id)])
            domain += [('user_id', '=', student.user_id.id),
                       ('state', 'in', ['in_progress', 'done'])]
            enrollments = request.env['op.course.enrollment'].sudo().search(domain)
        else:
            domain += [('user_id', '=', request.env.uid),
                       ('state', 'in', ['in_progress', 'done'])]
            enrollments = request.env['op.course.enrollment'].sudo().search(domain)
        data = self.my_corse_details(enrollments)
        data['search'] = search
        return request.render('openeducat_lms.my-courses', data)

    @http.route('''/course-detail/<model("op.course"):course>''', type='http',
                auth="public", sitemap=False, website=True)
    def course(self, course, search='', **kw):
        # domain = [course.id]
        if search:
            for srch in search:
                course = request.env['op.course'].sudo().search(
                    [('name', 'ilike', srch)])

        course = request.env['op.course'].sudo().browse([course.id])
        sections = request.env['op.course.section'].sudo().search(
            [('course_id', '=', course.id)], order='sequence asc')
        enrollment = request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', request.env.uid),
             ('course_id', '=', course.id),
             ('state', 'in', ['in_progress', 'done'])])
        completed_percentage = enrollment and enrollment.completed_percentage or 0
        ratings = request.env['rating.rating'].sudo().search([
            ('message_id', 'in', course.website_message_ids.ids)])
        rating_message_values = {
            record.message_id.id: record.rating for record in ratings}
        rating_course = course.rating_get_stats()
        values = {
            'course': course,
            'enrolled': enrollment and True or False,
            'completed_percentage': completed_percentage,
            'sections': sections,
            'user': request.env.user,
            'is_public_user': request.env.user == request.website.user_id,
            'rating_message_values': rating_message_values,
            'rating_course': rating_course
        }
        values.update(course.get_course_stats())
        return request.render('openeducat_lms.course_detail', values)

    @http.route(['''/course/<model("op.course"):course>''',
                 '''/course/<model("op.course"):course>/section/<model(\
                 "op.course.section"):section>''',
                 '''/course/<model("op.course"):course>/section/<model(\
                 "op.course.section"):section>/material/<model(\
                 "op.material"):material>''',
                 '''/course/<model("op.course"):course>/section/<model(\
                 "op.course.section"):section>/material/<model(\
                 "op.material"):material>/<next_mat>''',
                 '''/course/<model("op.course"):course>/section/<model(\
                 "op.course.section"):section>/material/<model(\
                 "op.material"):material>/result/<model(\
                 "op.quiz.result"):result>'''],
                type='http', auth="user", website=True)
    def get_course_material(self, course, section=None, material=None,
                            result=None, next_mat=0, **kwargs):

        enrollment = request.env['op.course.enrollment'].sudo().search(
            [('course_id', '=', course.id),
             ('user_id', '=', request.env.user.id)], limit=1)

        if not enrollment or not course.sudo().course_section_ids:
            return request.render('openeducat_lms.course_not_found')
        course_enroll_material_ref = request.env[
            'op.course.enrollment.material']
        if section:
            if material:
                if next_mat:
                    next_material = False

                    for x, y in enumerate(section.section_material_ids):
                        if material == y.material_id and x + int(next_mat) != len(
                                section.section_material_ids):
                            next_material = section.section_material_ids[
                                x + int(next_mat)].material_id
                            break

                    if not next_material:

                        next_section = self.get_next_section(course, section, next_mat)

                        if next_section:
                            return request.redirect('/course/%s/section/%s' % (
                                course.id, next_section.id))
                        else:
                            enrollment.sudo().write(
                                {'completion_date': fields.Datetime.now(),
                                 'state': 'done'})
                        return request.redirect('/my-courses')

                    next_material_access = self.check_material_access(
                        enrollment, next_material)
                    if not next_material_access:
                        return request.redirect(
                            '/course/%s/section/%s/material/%s/%s' % (
                                course.id, section.id,
                                next_material.id, next_mat))

                    cem_id = course_enroll_material_ref.sudo().search(
                        [('course_id', '=', course.id),
                         ('section_id', '=', section.id),
                         ('material_id', '=', next_material.id),
                         ('enrollment_id', '=', enrollment.id)], limit=1)

                    if cem_id:
                        cem_id.sudo().last_access_date = fields.Datetime.now()
                    else:
                        cem_id = self.create_course_enrollment_material(
                            enrollment.id, section.id, next_material.id)

                    return request.redirect(
                        '/course/%s/section/%s/material/%s' % (
                            course.id, section.id, next_material.id))
                else:
                    cem_id = course_enroll_material_ref.sudo().search([
                        ('course_id', '=', course.id),
                        ('section_id', '=', section.id),
                        ('material_id', '=', material.id),
                        ('enrollment_id', '=', enrollment.id)], limit=1)

                    if cem_id:
                        cem_id.sudo().last_access_date = fields.Datetime.now()
                    else:
                        cem_id = self.create_course_enrollment_material(
                            enrollment.id, section.id, material.id)

                    material = material
            else:
                if section.section_material_ids:
                    cem_id = course_enroll_material_ref.sudo().search(
                        [('course_id', '=', course.id),
                         ('section_id', '=', section.id),
                         ('material_id', '=',
                          section.section_material_ids[0].material_id.id),
                         ('enrollment_id', '=', enrollment.id)])
                    if not cem_id:
                        cem_id = self.create_course_enrollment_material(
                            enrollment.id, section.id,
                            section.section_material_ids[0].material_id.id)
                    else:
                        cem_id.sudo().last_access_date = fields.Datetime.now()
                    material = section.section_material_ids[0].material_id

                    material_access = self.check_material_access(
                        enrollment, material)
                    if not material_access:
                        return request.redirect(
                            '/course/%s/section/%s/material/%s/%s' % (
                                course.id, section.id, material.id, next_mat))
                else:
                    next_section = self.get_next_section(course, section, next_mat)
                    if next_section:
                        return request.redirect('/course/%s/section/%s' % (
                            course.id, next_section.id))
                    else:
                        return request.render(
                            'openeducat_lms.course_not_found')
        else:
            # Display first material of first section
            section_ids = request.env['op.course.section'].search(
                [('course_id', '=', course.id)], order='sequence asc')

            if section_ids and section_ids[0].section_material_ids:
                section = section_ids[0]

                cm_id = request.env['op.course.material'].search(
                    [('course_id', '=', course.id),
                     ('section_id', '=', section.id)],
                    order='sequence asc', limit=1)

                material_access = self.check_material_access(
                    enrollment, cm_id.material_id)
                if not material_access:
                    return request.redirect(
                        '/course/%s/section/%s/material/%s/%s' % (
                            course.id, section.id, cm_id.material_id.id, next_mat))

                cem_id = course_enroll_material_ref.sudo().search(
                    [('course_id', '=', course.id),
                     ('section_id', '=', section.id),
                     ('material_id', '=', cm_id.material_id.id),
                     ('enrollment_id', '=', enrollment.id)], limit=1)

                if cem_id:
                    cem_id.sudo().last_access_date = fields.Datetime.now()
                else:
                    cem_id = self.create_course_enrollment_material(
                        enrollment.id, section.id, cm_id.material_id.id)

                material = cm_id.material_id
            else:
                next_section = self.get_next_section(course, section, next_mat)
                if next_section:
                    return request.redirect(
                        '/course/%s/section/%s' % (course.id, next_section.id))
                else:
                    return request.render('openeducat_lms.course_not_found')

        related_materials = self.get_related_materials(course, enrollment)
        material = request.env['op.material'].sudo().browse([material.id])
        last_material = False
        if not self.get_next_section(course, section, next_mat):
            last_material = material == section.section_material_ids[-1:]. \
                material_id and True or False
        lms_full = request.httprequest.cookies.get('lms_full')
        data = {
            'course': course,
            'section': section,
            'material': material,
            'user': request.env.user,
            'related_materials': related_materials,
            'last_material': last_material,
            'embed_code': Markup(material.embed_code) if material.embed_code else False,
            'is_full': True if lms_full == 'full' else False
        }
        # ############ Material if type == Quiz ###########
        if material.sudo().material_type and \
                material.sudo().material_type == 'quiz':
            quiz_limit = 0
            result_val = False
            if material.sudo().quiz_id.no_of_attempt > 0 and not result:
                total_result_ids = 0
                attempt_ids = request.env['op.quiz.result'].search([
                    ('user_id', '=', request.env.uid),
                    ('quiz_id', '=', material.sudo().quiz_id.id)])

                for attempt in attempt_ids:
                    total_correct = attempt.total_correct
                    total_incorrect = attempt.total_incorrect
                    if not total_correct and not total_incorrect:
                        result_val = attempt
                    else:
                        total_result_ids += 1
                if material.sudo().quiz_id.no_of_attempt <= total_result_ids:
                    quiz_limit = 1
            if quiz_limit == 0 and not result:
                if not result_val:
                    result_val = material.sudo().quiz_id.get_result_id()
                data['exam'] = result_val.quiz_id
                data['result'] = result_val
                data['total_question'] = result_val.total_question
                data['course_val'] = course.id
                data['material_val'] = material.sudo().id
                data['section_val'] = section.id
            data['quiz_limit'] = quiz_limit
        is_result = 0
        # is_thanks = 0
        if result:
            is_result = 1
            if not result.quiz_id.show_result:
                pass
                # is_thanks = 1
            else:
                result_data = result.get_answer_data()
                for key in result_data.keys():
                    data.update({key: result_data[key]})
        data['is_result'] = is_result
        # data['is_thanks'] = is_thanks

        return request.render('openeducat_lms.material_detail_view', data)

    def check_material_access(self, enrollment, material):
        if not material.website_published:
            return False
        elif material.website_published and not material.auto_publish:
            return True
        elif material.website_published and material.auto_publish:
            if material.auto_publish_type == 'wait_until':
                wait_until_date = material.wait_until_date
                return wait_until_date < date.today() and True or False
            elif material.auto_publish_type == 'wait_until_duration':
                allowed = False
                enrollment_date = datetime.strptime(
                    str(enrollment.enrollment_date),
                    tools.DEFAULT_SERVER_DATETIME_FORMAT)
                if material.wait_until_duration_period == 'minutes':
                    access_time = enrollment_date + relativedelta(
                        minutes=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'hours':
                    access_time = enrollment_date + relativedelta(
                        hours=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'days':
                    access_time = enrollment_date + relativedelta(
                        days=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'weeks':
                    access_time = enrollment_date + relativedelta(
                        weeks=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'months':
                    access_time = enrollment_date + relativedelta(
                        months=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'years':
                    access_time = enrollment_date + relativedelta(
                        years=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                return allowed and True or False

    def create_course_enrollment_material(self, enrollment_id, section_id,
                                          material_id):
        cem_id = request.env['op.course.enrollment.material'].sudo().create(
            {'enrollment_id': enrollment_id,
             'section_id': section_id,
             'material_id': material_id,
             'completed': True,
             'completed_date': fields.Datetime.now(),
             'last_access_date': fields.Datetime.now()})
        return cem_id

    def get_related_materials(self, course, enrollment):
        data1 = {}
        data2 = {}
        enroll_material_ref = request.env['op.course.enrollment.material']
        if course.navigation_policy == 'free_learn':
            section_ids = request.env['op.course.section'].sudo().search([
                ('course_id', '=', course.id)], order='sequence asc')

            for x in section_ids:
                for y in x.section_material_ids:
                    cem_id = enroll_material_ref.sudo().search(
                        [('enrollment_id', '=', enrollment.id),
                         ('section_id', '=', x.id),
                         ('material_id', '=', y.material_id.id)], limit=1)
                    material_access = self.check_material_access(
                        enrollment, y.material_id)
                    if material_access:
                        if x not in data2:
                            data2[x] = {'material': {y.material_id: {
                                'completed': (cem_id and cem_id.completed
                                              ) and True or False}}}
                        else:
                            data2[x]['material'].update({y.material_id: {
                                'completed': (cem_id and cem_id.completed
                                              ) and True or False}})
            return data2
        else:
            cem_ids = enroll_material_ref.sudo().search(
                [('enrollment_id', '=', enrollment.id)],
                order='completed_date asc')

            for x in cem_ids:
                if x.section_id not in data1:
                    data1[x.section_id] = {'material': {
                        x.material_id: {'completed': x.completed}}}
                else:
                    data1[x.section_id]['material'].update(
                        {x.material_id: {'completed': x.completed}})
            return data1

    def get_next_section(self, course, section, next_mat):
        section_ids = request.env['op.course.section'].search(
            [('course_id', '=', course.id)], order='sequence asc')

        next_section = False
        for x, y in enumerate(section_ids):
            next_mat = next_mat if next_mat else 0
            if section == y and x + int(next_mat) != len(section_ids):
                next_section = section_ids[x + int(next_mat)]
                break

        return next_section

    @http.route('''/course/material/<model( \
                "op.material", "[('datas', '!=', False), ( \
                'material_type', '=', 'document')]"):material>/pdf_content''',
                type='http', auth="public", sitemap=False, website=True)
    def material_get_pdf_content(self, material):
        response = werkzeug.wrappers.Response()
        response.data = material.datas and base64.b64decode(
            material.datas) or b''
        response.mimetype = 'application/msword'
        return response

    # --------------------------------------------------
    # EMBED IN THIRD PARTY WEBSITES
    # --------------------------------------------------
    @http.route('/materials/embed/<int:material_id>', type='http',
                auth='public', website=True)
    def materials_embed(self, material_id, page="1", **kw):
        try:
            template = 'openeducat_lms.embed_material'
            material = request.env['op.material'].browse(material_id)
        except AccessError:
            template = 'openeducat_lms.embed_material_forbidden'
            material = request.env['op.material'].sudo().browse(material_id)
        return request.render(template, {'material': material})

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(
                    document_sudo.access_token, access_token):
                raise
        return document_sudo

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))

        report_sudo = request.env.ref(report_ref).sudo()

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(_("%s is not the reference of a report", report_ref))

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)(
            report_ref, [model.id], data={'report_type': report_type})[0]
        reporthttpheaders = [
            ('Content-Type',
             'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % \
                       (re.sub(r'\W+', '-', model._get_report_base_filename()))
            reporthttpheaders.append(
                ('Content-Disposition', content_disposition(filename)))
        return request.make_response(
            report, headers=reporthttpheaders)

    @http.route(['/certificates/<int:order_id>',
                 '/certificates/<int:student_id>/<int:order_id>'],
                type='http', auth="user", website=True)
    def portal_certificate_download(self, order_id, report_type=None, access_token=None,
                                    download=False, **kw):
        try:
            order_sudo = self._document_check_access('op.course.enrollment', order_id,
                                                     access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/certificate')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type,
                                     report_ref='openeducat_lms.certification_report',
                                     download=download)
        values = {
            'token': access_token,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
        }

        return request.render('openeducat_lms.certification_report_view', values)

    def _prepare_portal_layout_values(self):

        values = super(OpenEduCatLms, self). \
            _prepare_portal_layout_values()
        user = request.env.user

        certificate_count = request.env['op.course.enrollment'].sudo(). \
            search_count([('user_id', '=', user.id), ('state', '=', 'done')])
        values['certificate_count'] = certificate_count
        return values

    def _parent_prepare_portal_layout_values(self, student_id=None):
        val = super(OpenEduCatLms, self). \
            _parent_prepare_portal_layout_values(student_id)
        student = request.env['op.student'].sudo().search([('id', '=', student_id)])
        certificate_count = request.env['op.course.enrollment'].sudo(). \
            search_count([('user_id', '=', student.user_id.id),
                          ('state', '=', 'done')])
        val['certificate_count'] = certificate_count
        return val

    def get_search_domain_certificate(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', ('course_id', 'ilike', srch),
                    ('index', 'ilike', srch), ('enrollment_date', 'ilike', srch),
                    ('completion_date', 'ilike', srch)]
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

    @http.route(['/certificate',
                 '/certificate/<int:student_id>',
                 '/certificate/page/<int:page>',
                 '/certificate/<int:student_id>/page/<int:page>'],
                type="http", auth="user", website=True)
    def get_certificate_overview(
            self, date_begin=None, student_id=None, date_end=None,
            page=0, search='', ppg=False, sortby=None, filterby=None,
            search_in='content', groupby='none', **post):
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
            'index': {'label': _('Index'), 'order': 'index'},
            'course_id': {'label': _('Course'), 'order': 'course_id'},
            'enrollment_date': {'label': _('Enroll Date'), 'order': 'enrollment_date'},
            'completion_date': {'label': _('CMP Date'), 'order': 'completion_date'},
        }
        if not sortby:
            sortby = 'index'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")]
                         for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content',
                        'label': Markup(_('Search in Index <span class="nolabel">'
                                          ' (in Content)</span>'))},
            'course_id': {'input': 'Course',
                          'label': _('Search in Course')},
            'enrollment_date': {'input': 'Enroll Date',
                                'label': _('Search in Enroll Date')},
            'completion_date': {'input': 'CMP Date',
                                'label': _('Search in CMP Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'content'):
                search_domain = expression.OR(
                    [search_domain, [('index', 'ilike', search)]])
            if search_in in ('all', 'index'):
                search_domain = expression.OR(
                    [search_domain, [('course_id', 'ilike', search)]])
            if search_in in ('all', 'enrollment_date'):
                search_domain = expression.OR(
                    [search_domain, [('enrollment_date', 'ilike', search)]])
            if search_in in ('all', 'completion_date'):
                search_domain = expression.OR(
                    [search_domain, [('completion_date', 'ilike', search)]])
            domain += search_domain

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        domain += self.get_search_domain_certificate(search, attrib_values)

        if student_id:
            keep = QueryURL('/certificate/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))
            student = request.env['op.student'].sudo().search(
                [('id', '=', student_id)])

            domain += [('user_id', '=', student.user_id.id), ('state', '=', 'done')]
            total = request.env['op.course.enrollment'].sudo().search_count(
                domain)

            pager = portal_pager(
                url="/certificate/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/certificate', search=search, attrib=attrib_list,
                            order=post.get('order'))

            domain += [('user_id', '=', request.env.uid), ('state', '=', 'done')]
            total = request.env['op.course.enrollment'].sudo().search_count(
                domain)

            pager = portal_pager(
                url="/certificate",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_in': search_in},
                total=total,
                page=page,
                step=ppg
            )
        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')
            certificate_result = request.env['op.course.enrollment'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        else:
            certificate_result = request.env['op.course.enrollment'].sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        data = []
        for res in certificate_result:
            data.append({
                'id': res.id,
                'index': res.index,
                'name': res.course_id,
                'enroll_date': res.enrollment_date,
                'cmp_date': res.completion_date,
                'certi': res.get_portal_url(report_type='pdf', download=True),
            })
        post['result_data'] = data
        if student_id:
            val.update({
                'date': date_begin,
                'result_data': data,
                'page_name': 'Certificate',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'stud_id': student_id,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/certificate/%s' % student_id,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,
            })
            return http.request.render('openeducat_lms.certicate_portal_view', val)
        else:
            values.update({
                'date': date_begin,
                'result_data': data,
                'page_name': 'Certificate',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/certificate',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,
            })

            return http.request.render('openeducat_lms.certicate_portal_view', values)

    # Dashboard Controllers

    @http.route('/openeducat_lms/fetch_course', type='json', auth='user')
    def fetch_openeducat_lms_course(self):
        course_ids = request.env['op.course'].search_read(
            [('online_course', '=', True)], ['id', 'name'], order='name')
        return {'course_ids': course_ids}

    @http.route('/openeducat_lms/get_lms_dash_data', type='json', auth='user')
    def compute_lms_course_dashboard_data(self, course_id=None):
        enrolled_users = 0
        days_since_launch = 0
        course_duration = 0
        training_material = 0
        course_to_begin = 0
        course_in_progress = 0
        course_completed = 0

        if course_id:
            course = request.env['op.course'].browse([int(course_id)])
            enrolled_users = course.enrolled_users
            days_since_launch = course.days_since_launch
            course_duration = course.display_time
            training_material = course.training_material
            course_to_begin = course.course_to_begin
            course_in_progress = course.course_in_progress
            course_completed = course.course_completed

        return {'enrolled_users': enrolled_users,
                'days_since_launch': days_since_launch,
                'course_duration': course_duration,
                'training_material': training_material,
                'course_to_begin': course_to_begin,
                'course_in_progress': course_in_progress,
                'course_completed': course_completed}

    @http.route('/openeducat_lms/compute_openeducat_graph',
                type='json', auth='user')
    def compute_openeducat_lms_graph(self):
        data = []
        last_day = datetime.today().replace(day=calendar.monthrange(
            datetime.today().year, datetime.today().month)[1])
        for d in range(1, last_day.day + 1):
            label = str(d)
            start_date = datetime.now().replace(
                day=d).strftime('%Y-%m-%d 00:00:00')
            end_date = datetime.now().replace(
                day=d).strftime('%Y-%m-%d 23:59:59')
            count = request.env['op.course.enrollment'].sudo().search_count(
                [('enrollment_date', '>=', start_date),
                 ('enrollment_date', '<=', end_date)])
            data.append({'label': label,
                         'value': count and count or 0})
        return data

    @http.route('/openeducat_lms/compute_openeducat_course_graph',
                type='json', auth='user')
    def compute_openeducat_lms_course_graph(self, course_id=None):
        data = []
        if course_id:
            last_day = datetime.today().replace(
                day=calendar.monthrange(datetime.today().year,
                                        datetime.today().month)[1])
            for d in range(1, last_day.day + 1):
                start_date = datetime.now().replace(
                    day=d).strftime('%Y-%m-%d 00:00:00')
                end_date = datetime.now().replace(
                    day=d).strftime('%Y-%m-%d 23:59:59')
                count = request.env[
                    'op.course.enrollment'].sudo().search_count(
                    [('course_id', '=', int(course_id)),
                     ('enrollment_date', '>=', start_date),
                     ('enrollment_date', '<=', end_date)])
                data.append({'label': str(d), 'value': count and count or 0})
        return data

    @http.route(['/my/course'], type='http', auth='public', website=True)
    def my_lms_profile(self, **post):
        enrollments = request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', request.env.uid),
             ('state', 'in', ['in_progress', 'done'])])
        data = {'user': request.env.user}
        if enrollments:
            data = self.my_corse_details(enrollments)
        return request.render("openeducat_lms.my_profile", data)

    @http.route('/material-edit/<model("op.material"):material>', type='http',
                website=True, auth='user')
    def edit_web_page_content_material(self, material):
        if material.material_type != 'webpage':
            NotFound()

        return request.render('openeducat_lms.edit_web_page_material', {
            'material': material,
            'edit_in_backend': True,
            # 'main_object': material,
        })


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        """ Add sales documents to main account page """
        response = super(CustomerPortal, self).home(**kw)
        count = request.env['op.course.enrollment'].sudo().search_count(
            [('user_id', '=', request.env.uid),
             ('state', 'in', ['in_progress', 'done'])])
        response.qcontext.update({
            'course_count': count
        })
        return response


class Lms(http.Controller):
    @http.route('/get/code/<string:survey_token>', type='http', auth='public',
                website=True, sitemap=False)
    def get_code(self):
        return request.render('openeducat_lms.embed_ppt_material_details', {})
