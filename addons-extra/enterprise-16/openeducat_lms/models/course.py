# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json
import math
import urllib.parse as urlparse
from datetime import date, datetime

from odoo import api, fields, models
from odoo.tools.translate import html_translate

from odoo.addons.http_routing.models.ir_http import slug


def float_time_convert(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    return (factor * int(math.floor(val)), int(round((val % 1) * 60)))


class OpCourse(models.Model):
    _name = "op.course"
    _inherit = ["op.course", "mail.thread",
                "rating.mixin", "website.published.mixin",
                "website.searchable.mixin"]
    _description = "LMS Course"

    online_course = fields.Boolean('Online Course')
    sequence = fields.Integer(default=10, help='Display order')
    active = fields.Boolean(default=True)
    short_description = fields.Char('Short Description', size=80)
    full_description = fields.Html('Full Description',
                                   translate=html_translate,
                                   sanitize_attributes=False)
    thumbnail_type = fields.Selection([('video', 'Video'),
                                       ('url', 'URL')])
    thumb_video = fields.Binary('Thumbnail Video')
    thumb_url = fields.Char('Thumbnail Youtube Url')
    thumb_document = fields.Char('Thumbnail Document')
    image_1920 = fields.Image('Image', attachment=True)
    image_medium = fields.Image('Medium', compute="_compute_get_image",
                                store=True, attachment=True)
    image_thumb = fields.Image('Thumbnail', compute="_compute_get_image",
                               store=True, attachment=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)
    certificate = fields.Boolean(string='Certificate')
    background = fields.Image('Background Image', attachment=True)
    title = fields.Boolean('Title', default=True)
    certi_title = fields.Char('Certificate Title')
    certi_date = fields.Boolean('Certificate Date', default=True)
    certi_num = fields.Boolean('Certificate Number', default=True)

    @api.depends('image_1920')
    def _compute_get_image(self):
        for record in self:
            if record.image_1920:
                record.image_medium = record.image_1920

                record.image_thumb = record.image_1920
            else:
                record.image_medium = False
                record.image_thumb = False

    faculty_ids = fields.Many2many('op.faculty', string='Instructor')
    suggested_course_ids = fields.Many2many(
        'op.course', 'course_suggested_course_rel', 'course_id',
        'suggested_course_id', string='Courses')
    user_id = fields.Many2one('res.users', 'Create By', required=True,
                              default=lambda self: self.env.uid)
    user_ids = fields.Many2many('res.users',
                                'course_user_rel',
                                'course_id',
                                'user_id', 'Users')
    category_ids = fields.Many2many('op.course.category',
                                    'course_category_rel',
                                    'course_id',
                                    'category_id', 'Categories')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Confirm'),
                              ('closed', 'Closed')], 'State', default="draft")
    promoted_material_id = fields.Many2one(
        'op.material', string='Featured Material')
    navigation_policy = fields.Selection([
        ('free_learn', 'Free Learning Path'),
        ('seq_learn', 'Sequential Learning Path')], 'Navigation Policy',
        default='free_learn')
    visibility = fields.Selection([
        ('public', 'Everyone'),
        ('logged_user', 'Only logged in User'),
        ('invited_user', 'Only Invited User')], 'Visibility Policy',
        default="public")
    course_section_ids = fields.One2many(
        'op.course.section', 'course_id', 'Sections')
    course_enrollment_ids = fields.One2many(
        'op.course.enrollment', 'course_id', 'Enrollments')
    enrollment_user_ids = fields.Many2many('res.users',
                                           'course_enrolled_user_rel',
                                           'course_id',
                                           'user_id', store=True,
                                           compute='_compute_enrolled_users',
                                           string='Enrolled Users')
    invited_users_ids = fields.Many2many(
        'res.users', 'course_invited_user_rel', 'plan_id',
        'user_id', 'Invited Users')
    type = fields.Selection([('free', 'Free'), ('paid', 'paid')],
                            'Course', default='free')
    language = fields.Char('Course Language', default='English')
    website_message_ids = fields.One2many(
        'mail.message', 'res_id',
        domain=lambda self: ['&', ('model', '=', self._name),
                             ('message_type', '=', 'comment')],
        string='Website Comments')
    total_time = fields.Float('Total Time (HH:MM)',
                              compute='_compute_total_times')
    display_time = fields.Char('Display Time',
                               compute='_compute_display_time')
    confirm_date = fields.Date('Confirm Date')
    is_published = fields.Boolean(
        'Is Published', copy=False,
        default=lambda self: self._default_is_published())

    def _default_department(self):
        if self.env.context.get('default_online_course'):
            return False
        else:
            return self.env.user.dept_id and self.env.user.dept_id.id or False

    department_id = fields.Many2one('op.department', 'Department',
                                    default=lambda self: self._default_department())

    def _compute_get_section(self):
        for record in self:
            record.section_count = self.env['op.course.section'].search_count(
                [('course_id', 'in', self.ids)])

    section_count = fields.Integer(string='Section Count',
                                   compute='_compute_get_section', readonly=True)

    def _compute_total_times(self):
        for course in self:
            if course.course_section_ids:
                for cs in course.course_section_ids:
                    course.total_time += cs.total_time
            else:
                course.total_time = 0.0

    @api.depends('course_enrollment_ids')
    def _compute_enrolled_users(self):
        for course in self:
            enrolled_ids = [x.user_id.id for x in course.course_enrollment_ids]
            course.enrollment_user_ids = [(6, 0, enrolled_ids)]

    def _compute_display_time(self):
        for course in self:
            data = float_time_convert(course.total_time)
            hour = data[0] <= 9 and '0' + str(data[0]) or str(data[0])
            minute = data[1] <= 9 and '0' + str(data[1]) or str(data[1])
            course.display_time = str(hour) + ':' + str(minute)

    def action_confirm(self):
        for obj in self:
            obj.state = 'open'
            obj.confirm_date = fields.Date.today()
        return True

    def action_draft(self):
        for obj in self:
            obj.state = 'draft'
        return True

    def action_closed(self):
        for obj in self:
            obj.state = 'closed'
        return True

    def float_time_convert(self, float_val=1):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return (factor * int(math.floor(val)), int(round((val % 1) * 60)))

    # Dashboard Calculation
    def _compute_kanban_dashboard_graph(self):
        for record in self:
            record.kanban_lms_course_dashboard_graph = json.dumps(
                record.get_lms_bar_graph_datas())

    def _compute_graph_data(self):
        for course in self:
            course_enroll_ref = self.env['op.course.enrollment']
            days_since_launch = 0
            enrolled_users = course_enroll_ref.search_count([
                ('course_id', '=', course.id)])
            course = self.env['op.course'].browse([course.id])
            if course.confirm_date:
                confirm_date = fields.Datetime.from_string(
                    course.confirm_date).date()
                days_since_launch = (date.today() - confirm_date).days
            training_material = self.env['op.course.material'].search_count([
                ('course_id', '=', course.id)])
            course_to_begin = course_enroll_ref.search_count([
                ('course_id', '=', course.id), ('state', '=', 'draft')])
            course_in_progress = course_enroll_ref.search_count([
                ('course_id', '=', course.id), ('state', '=', 'in_progress')])
            course_completed = course_enroll_ref.search_count([
                ('course_id', '=', course.id), ('state', '=', 'done')])
            course.enrolled_users = enrolled_users
            course.days_since_launch = days_since_launch
            course.training_material = training_material
            course.course_to_begin = course_to_begin
            course.course_in_progress = course_in_progress
            course.course_completed = course_completed

    enrolled_users = fields.Integer(
        compute="_compute_graph_data", string='Enrolled User')
    days_since_launch = fields.Integer(
        compute="_compute_graph_data", string='Days Since Launch')
    training_material = fields.Integer(
        compute="_compute_graph_data", string='Training Material')
    course_to_begin = fields.Integer(
        compute="_compute_graph_data", string='Course To Begin')
    course_in_progress = fields.Integer(
        compute="_compute_graph_data", string='Course In Progress')
    course_completed = fields.Integer(
        compute="_compute_graph_data", string='Course Completed')
    kanban_lms_course_dashboard_graph = fields.Text(
        compute='_compute_kanban_dashboard_graph')
    level_id = fields.Many2one('op.course.level', string='Level')

    @api.model
    def _search_get_detail(self, website, order, options):
        with_description = options['displayDescription']
        search_fields = ['name']
        fetch_fields = ['id', 'name', 'website_url']
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'website_url': {'name': 'website_url', 'type': 'text'},
        }
        if with_description:
            search_fields.append('short_description')
            fetch_fields.append('short_description')
            mapping['description'] = {'name': 'short_description',
                                      'type': 'text', 'match': True}
        return {
            'model': 'op.course',
            'base_domain': [[('online_course', '=', True)]],
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-rss-square',
            'order': 'name desc, id desc' if 'name desc' in order else
                     'name asc, id desc',
        }

    @api.depends('name')
    def _compute_website_url(self):
        super(OpCourse, self)._compute_website_url()
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        for course in self:
            course.website_url = '%s/course-detail/%s' % (base_url, slug(course))

    def get_course_stats(self):
        total_videos, total_lecture, total_video_hours = 0, 0, 0.0
        total_overall_lecture = 0
        for section in self.course_section_ids:
            for material in section.section_material_ids:
                if material.material_id:
                    total_overall_lecture += 1
                    if material.material_id.material_type == 'video':
                        total_videos += 1
                        total_video_hours += material.material_id.total_time
                    else:
                        total_lecture += 1
        return {
            'total_videos': total_videos,
            'total_lecture': total_lecture,
            'total_video_hours': total_video_hours,
            'total_overall_lecture': total_overall_lecture,
        }

    @api.onchange('thumb_url')
    def _onchange_thumb_document(self):
        for rec in self:
            if rec.thumbnail_type == 'url':
                url_data = urlparse.urlparse(rec.thumb_url)
                query = urlparse.parse_qs(url_data.query)
                rec.thumb_document = query.get('v', False) and query['v'][0] or False
                if not rec.thumb_document:
                    rec.thumb_document = url_data.path and url_data.path[1:] or False

    def get_lms_bar_graph_datas(self):
        data = []
        for course in self:
            for d in range(1, (fields.date.today().day) + 1):
                label = str(d)
                start_date = datetime.now().replace(
                    day=d).strftime('%Y-%m-%d 00:00:00')
                end_date = datetime.now().replace(
                    day=d).strftime('%Y-%m-%d 23:59:59')
                count = self.env['op.course.enrollment'].search_count(
                    [('course_id', '=', course.id),
                     ('enrollment_date', '>=', start_date),
                     ('enrollment_date', '<=', end_date)])
                data.append({'label': label,
                             'value': count and count or 0})
        return [{'values': data}]

    def action_lms_onboarding_course_layout(self):
        self.env.user.company_id.onboarding_lms_course_layout_state = 'done'

    def action_view_material(self):
        action = self.env.ref('openeducat_lms.'
                              'act_open_op_course_material_view').read()[0]
        action['domain'] = [('id', 'in', self.course_section_ids.
                             section_material_ids.material_id.ids)]
        return action

    def action_view_section(self):
        action = self.env.ref('openeducat_lms.act_open'
                              '_op_course_section_view').read()[0]
        action['context'] = {
            'course_id': self.id
        }
        action['domain'] = [('course_id', "=", self.id)]

        value = {
            'name': 'Course Section Line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'op.course.section',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_course_id': self.id},
            'domain': [('course_id', "=", self.id)]

        }
        return value

    def action_view_users(self):
        action = self.env.ref('openeducat_lms.'
                              'act_open_op_course_enrollment_view').read()[0]
        action['domain'] = [('id', 'in', self.course_enrollment_ids.ids)]
        return action

    def action_course_completed(self):
        action = self.env.ref('openeducat_lms.'
                              'act_open_op_course_enrollment_view').read()[0]
        action['domain'] = [('id', 'in', self.course_enrollment_ids.ids),
                            ('state', '=', 'done')]
        return action


class OpCourseSection(models.Model):
    _name = "op.course.section"
    _rec_name = "name"
    _order = "sequence asc"
    _description = "LMS Course Section"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Section', required=True)
    course_id = fields.Many2one('op.course', 'Course', required=True,
                                ondelete="cascade")
    section_material_ids = fields.One2many('op.course.material',
                                           'section_id', 'Section Materials')
    total_time = fields.Float('Total Time (HH:MM)',
                              compute='_compute_total_time')
    display_time = fields.Char('Display Time',
                               compute='_compute_display_time')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def _compute_get_section_material(self):
        for record in self:
            record.material_count = self.env['op.course.material'].search_count(
                [('section_id', 'in', self.ids)])

    material_count = fields.Integer(string='Material Count',
                                    compute='_compute_get_section_material',
                                    readonly=True)

    def action_view_section_material(self):
        action = self.env.ref('openeducat_lms.act_open_op_course'
                              '_section_material_view').read()[0]
        action['context'] = {
            'section_id': self.id
        }
        action['domain'] = [('section_id', "=", self.id)]

        value = {
            'name': 'Course Section Material Line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'op.course.material',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_section_id': self.id},
            'domain': [('section_id', "=", self.id)]

        }
        return value

    def _compute_total_time(self):
        for section in self:
            if section.section_material_ids:
                for cm in section.section_material_ids:
                    section.total_time += cm.material_id.total_time
            else:
                section.total_time = 0.0

    def _compute_display_time(self):
        for section in self:
            data = float_time_convert(section.total_time)
            hour = data[0] <= 9 and '0' + str(data[0]) or str(data[0])
            minute = data[1] <= 9 and '0' + str(data[1]) or str(data[1])
            section.display_time = str(hour) + ':' + str(minute)


class OpCourseMaterial(models.Model):
    _name = "op.course.material"
    _rec_name = "material_id"
    _order = "sequence asc"
    _description = "LMS Course Materials"

    sequence = fields.Integer('Sequence', required=True)
    section_id = fields.Many2one('op.course.section', 'Section',
                                 required=True, ondelete="cascade")
    course_id = fields.Many2one(related='section_id.course_id',
                                string='Course')
    material_id = fields.Many2one('op.material', 'Material', required=True)
    preview = fields.Boolean('Preview')
    total_time = fields.Float(related='material_id.total_time',
                              string='Total Time (HH:MM)')
    display_time = fields.Char('Display Time',
                               compute='_compute_display_time')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def _compute_display_time(self):
        for material in self:
            data = float_time_convert(material.total_time)
            hour = data[0] <= 9 and '0' + str(data[0]) or str(data[0])
            minute = data[1] <= 9 and '0' + str(data[1]) or str(data[1])
            material.display_time = str(hour) + ':' + str(minute)
