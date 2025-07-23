# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import base64
import json

from psycopg2 import IntegrityError

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


class OnlineJob(http.Controller):
    @http.route('/campus/jobs', type='http', auth='public', website=True)
    def online_job_post(self, search='', **kwargs):
        domain = []
        if search:
            domain += [('job_post', 'ilike', search)]
        job_post_id = request.env['op.job.post'].search(domain)

        return request.render('openeducat_job_enterprise.job_post_list', {
            'job_post_id': job_post_id
        })

    @http.route(
        '/job_post/detail/<model("op.job.post"):job_post_id>',
        type='http', auth='public', website=True)
    def job_post_detail(self, job_post_id, **kwargs):

        return http.request.render('openeducat_job_enterprise.jobpost_detail',
                                   {'job_post_id': job_post_id})

    @http.route(
        '/job_post/detail/post/<model("op.job.post"):job_description_id>',
        type='http', auth='public', website=True)
    def job_description_detail(self, job_description_id, **kwargs):

        return http.request.render('openeducat_job_enterprise.'
                                   'jobpost_description',
                                   {'job_description_id': job_description_id})

    # @http.route(
    #     '/job/post/apply/<model("op.job.post"):'
    #     'job_post_id>', type='http', auth="user", website=True)
    # def online_jobs_apply(self, job_post_id, **kwargs):
    #     return request.render("openeducat_job_enterprise.apply", {
    #         'job_post_id': job_post_id,
    #     })

    @http.route('/form/submit<string:model_name>',
                type='http', auth="public", sitemap=False,
                methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        model_record = request.env['ir.model'].sudo().search(
            [('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps(False)

        try:
            data = self.extract_value(model_record, request.params)
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})

        try:
            if kwargs.get('activity'):
                activity_id = request.env['op.activity.announcement'].search(
                    [('id', '=', int(kwargs.get('activity')))])
                data['record'].update({'activity_id': activity_id.id})
            if kwargs.get('job_post'):
                job_post_id = request.env['op.job.post'] \
                    .search([('id', '=', int(kwargs.get('job_post')))])
                data['record'].update({'post_id': job_post_id.id})

            id_record = self.insert_record(request,
                                           model_record, data['record'],
                                           data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachments(model_record,
                                        id_record, data['attachments'])
        except IntegrityError:
            return json.dumps(False)

        return json.dumps({'id': id_record})

    def extract_value(self, model, values):

        data = {
            'record': {},
            'attachments': [],
            'custom': '',
            'meta': '',
        }

        authorized_fields = model.sudo()._get_form_writable_fields()

        for field_name, field_value in values.items():
            if hasattr(field_value, 'filename'):
                field_name = field_name.rsplit('[', 1)[0]

                if field_name in authorized_fields and \
                        authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] \
                        = base64.b64encode(field_value.read())
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)
        return data

    def insert_record(self, request, model, values, custom, meta=None):
        user = request.env.user
        student_id = request.env['op.student'].sudo() \
            .search([('user_id', '=', user.id)])
        values.update({'user_id': student_id.id})
        model_name = model.sudo().model
        record = request.env[model_name].sudo() \
            .with_context(mail_create_nosubscribe=True).create(values)

        return record.id

    def insert_attachments(self, model, id_record, files):
        attachment_ids = []
        model_name = model.sudo().model
        record = model.env[model_name].browse(id_record)
        authorized_fields = model.sudo()._get_form_writable_fields()
        for file in files:
            custom_field = file.field_name not in authorized_fields
            attachment_value = {
                'name': file.filename,
                'datas': base64.encodebytes(file.read()),
                # 'name': file.filename,
                'res_model': model_name,
                'res_id': record.id,
            }
            attachment_id = request.env['ir.attachment'].sudo() \
                .create(attachment_value)
            if attachment_id and not custom_field:
                record.sudo()[file.field_name] = [(4, attachment_id.id)]
            else:
                attachment_ids.append(attachment_id.id)
