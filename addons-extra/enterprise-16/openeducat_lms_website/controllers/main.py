# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import base64
import logging

import werkzeug

from odoo import SUPERUSER_ID, _, http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.osv import expression
from odoo.tools import consteq

from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)

PPG = 12  # Products Per Page
PPR = 4  # Products Per Row


class OpenEduCatLms(http.Controller):
    @http.route('''/course-detail/<model("op.course"):course>''', type='http',
                auth="public", sitemap=False, website=True)
    def course(self, course, **kw):
        course = request.env['op.course'].sudo().browse([course.id])
        sections = request.env['op.course.section'].sudo().search(
            [('course_id', '=', course.id)], order='sequence asc')
        enrollment = request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', request.env.uid),
             ('course_id', '=', course.id),
             ('state', 'in', ['in_progress', 'done'])])
        completed_percentage = enrollment and \
            enrollment.completed_percentage or 0
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

    def _get_new_course_section_values(self, course, name, sequence):
        return {
            'name': name,
            'course_id': course.id,
            'sequence': sequence,
        }

    @http.route('''/course/material/<model( \
                "op.material", "[('datas', '!=', False), ( \
                'material_type', '=', 'document')]"):material>/pdf_content''',
                type='http', auth="public", sitemap=False, website=True)
    def material_get_pdf_content(self, material):
        response = werkzeug.wrappers.Response()
        response.data = material.datas and \
            base64.b64decode(material.datas) or b''
        response.mimetype = 'application/pdf'
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

    @http.route('/openeducat_lms/fetch_course', type='json', auth='user')
    def fetch_openeducat_lms_course(self):
        course_ids = request.env['op.course'].search_read(
            [('online_course', '=', True)], ['id', 'name'], order='name')
        return {'course_ids': course_ids}

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

    @http.route('/course/section/add', type="http", website=True, auth="user")
    def course_section_add(self, channel_id, name, sequence):
        channel = request.env['op.course'].browse(int(channel_id))

        request.env['op.course.section'].create(self._get_new_course_section_values(
            channel, name, sequence))

        return werkzeug.utils.redirect("/course-detail/%s" % (slug(channel)))

    @http.route(['/course/section/search_read'], type='json', auth='user',
                methods=['POST'], website=True)
    def slide_category_search_read(self, fields, domain):
        category_slide_domain = domain if domain else []
        category_slide_domain = expression.AND([category_slide_domain])
        can_create = request.env['op.course.section'].check_access_rights(
            'create', raise_exception=False)
        return {
            'read_results': request.env['op.course.section'].search_read(
                category_slide_domain, fields),
            'can_create': can_create,
        }

    @http.route(['/courses/add_material'], type='json', auth='user',
                methods=['POST'], website=True)
    def create_slide(self, *args, **post):
        if post.get('datas'):
            file_size = len(post['datas']) * 3 / 4  # base64
            if (file_size / 1024.0 / 1024.0) > 25:
                return {'error': _('File is too big. File size cannot exceed 25MB')}

        values = {fname: post[fname] for fname in self._get_valid_slide_post_values()
                  if post.get(fname)}

        try:
            channel = request.env['op.course'].browse(values['course_id'])
            can_upload = channel.can_upload
            can_publish = channel.can_publish
        except (UserError, AccessError) as e:
            _logger.error(e)
            return {'error': e.name}
        else:
            if not can_upload:
                return {'error': _('You cannot upload on this channel.')}

        if post.get('duration'):
            values['total_time'] = int(post['duration']) / 60
        if post.get('material_type') == 'video':
            document_type, document_id = request.env['op.material'].\
                _find_document_data_from_url(post['url'])
            values['document_id'] = document_id
        if post.get('category_id'):
            category_id = post['category_id'][0]

        try:
            values['user_id'] = request.env.uid
            values['is_published'] = values.get('is_published', False) and can_publish
            slide = request.env['op.material'].sudo().create(values)
        except (UserError, AccessError) as e:
            _logger.error(e)
            return {'error': e.name}
        except Exception as e:
            _logger.error(e)
            return {'error': _(
                'Internal server error, please try again later or '
                'contact administrator.\nHere is the error message: %s') % e}

        material_seq = request.env['op.course.section'].search([
            ('id', 'in', post['category_id'])])
        material_seq.seq = material_seq.seq + 1
        section_material = request.env['op.course.material'].create({
            'sequence': material_seq.seq,
            'section_id': category_id,
            'material_id': slide.id

        })

        redirect_url = "%s" % (channel.id)
        if slide.material_type == "quiz":
            action_id = request.env.ref('openeducat_lms.'
                                        'act_open_op_course_material_view').id
            redirect_url = '/web#id=%s&action=%s&model=op.material&view_type=form' \
                           % (slide.id, action_id)

        if slide.material_type == "webpage":
            redirect_url = '/material-edit/%s?enable_editor=1' % slug(slide)

        return {
            'section_material_ids': section_material,
            'url': redirect_url,
            'slide_id': slide.id,
            'category_id': slide.category_id
        }

    def _get_valid_slide_post_values(self):
        return ['name', 'url', 'material_type', 'course_id', 'is_preview',
                'datas', 'description', 'image_1920', 'is_published']

    @http.route(['/course/prepare_preview'], type='json', auth='user',
                methods=['POST'], website=True)
    def prepare_preview(self, **data):
        Slide = request.env['op.material']
        document_type, document_id = Slide._find_document_data_from_url(data['url'])
        preview = {}
        if not document_id:
            preview['error'] = _('Please enter valid youtube or google doc url')
            return preview
        existing_slide = Slide.search([('course_id', '=', int(data['course_id'])),
                                       ('document_id', '=', document_id)],
                                      limit=1)
        if existing_slide:
            preview['error'] = _(
                'This video already exists in this course on the following slide: %s')\
                % existing_slide.name
            return preview
        values = Slide._parse_document_url(data['url'], only_preview_fields=True)
        if values.get('error'):
            preview['error'] = _(
                'Could not fetch data from url. '
                'Document or access right not available.'
                '\nHere is the received response: %s') % values['error']
            return preview
        return values
