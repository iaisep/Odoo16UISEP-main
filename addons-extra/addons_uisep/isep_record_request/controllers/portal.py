import base64
import logging

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        user_id = request.env.uid
        current_user = request.env['res.users'].sudo().browse(user_id)
        # values['requests_quantity'] = request.env['record.request'].sudo().search_count([
        #     ('partner_id', '=', current_user.partner_id.id),
        #     ('op_admission_id.state', '=', 'done')
        # ])  # FIXME: CUANDO HAY 0 NO SE MUESTRA :(
        values['documents_quantity'] = len(current_user.partner_id.ir_attachment_ids)
        return values

    @http.route(['/my/requests', '/my/requests/page/<int:page>'], type='http', methods=['GET'], auth='public',
                website=True)
    def record_request_list_view(self, page=1, **kwargs):
        step = 10
        record_request_model = request.env['record.request'].sudo()
        user_id = request.env.uid
        current_user = request.env['res.users'].sudo().browse(user_id)
        domain = [
            ('partner_id', '=', current_user.partner_id.id),
            ('op_admission_id.state', '=', 'done')
        ]
        my_requests_quantity = record_request_model.search_count(domain)
        page_detail = pager(
            url='/my/requests',
            total=my_requests_quantity,
            page=page,
            step=step
        )
        my_requests = record_request_model.search(domain, limit=step, offset=page_detail['offset'])
        success_message = request.params.get('success_message', False)
        error_message = request.params.get('error_message', False)
        values = {
            'my_requests': my_requests,
            'page_name': 'request_list_view',
            'pager': page_detail,
            'success_message': success_message,
            'error_message': error_message
        }
        return request.render('isep_record_request.record_request_list_view', values)

    @http.route(['/my/requests/<int:record_request_id>'], type='http', methods=['GET'], auth='public', website=True)
    def record_request_form_view(self, record_request_id, **kwargs):
        record_request_model = request.env['record.request'].sudo()
        current_request = record_request_model.browse(record_request_id)
        values = {
            'current_request': current_request,
            'page_name': 'record_request_form_view'
        }
        user_id = request.env.uid
        current_user = request.env['res.users'].sudo().browse(user_id)
        record_request_ids = record_request_model.search([
            ('partner_id', '=', current_user.partner_id.id),
            ('op_admission_id.state', '=', 'done')
        ]).ids
        record_request_index = record_request_ids.index(record_request_id)
        values.update({
            'prev_record': record_request_index != 0 and f'/my/requests/{record_request_ids[record_request_index - 1]}',
            'next_record': record_request_index < len(record_request_ids) - 1 and f'/my/requests/{record_request_ids[record_request_index + 1]}'
        })
        return request.render('isep_record_request.record_request_form_view', values)

    @http.route(['/my/admissions'], type='http', methods=['GET'], auth='public', website=True)
    def admission_form_view(self, **kwargs):
        user_id = request.env.uid
        current_user = request.env['res.users'].sudo().browse(user_id)
        admissions = request.env['op.admission'].sudo().search([
            ('partner_id', '=', current_user.partner_id.id),
            ('state', '=', 'done')
        ])
        values = {
            'page_name': 'admission_form_view',
            'admissions': admissions
        }
        return request.render('isep_record_request.admission_form_view', values)

    @http.route(['/my/requests/new_request'], type='http', methods=['GET', 'POST'], auth='public', website=True)
    def new_request_form_view(self, **kwargs):
        if request.httprequest.method == 'GET':
            op_admission_model = request.env['op.admission'].sudo()
            values = {'page_name': 'new_request_form_view'}
            admission_id = kwargs.get('admissions', False)
            if admission_id:
                admission = op_admission_model.browse(int(admission_id))
                values.update({
                    'admission': admission,
                    'partner_id': admission.partner_id,
                    'batch_id': admission.batch_id,
                    'course_id': admission.course_id,
                    'application_number': admission.application_number
                })
            return request.render('isep_record_request.new_request_form_view', values)
        elif request.httprequest.method == 'POST':
            url = self.create_record_request(kwargs)
            return request.redirect(url)

    def create_record_request(self, kwargs):
        '''
            Create a new record request.
            :param kwargs: Arguments to create the new record request.
            :type kwargs: Dictionary.
            :return: A string that represents the url to be redirected.
            :rtype: str
        '''
        op_admission_id = int(kwargs.get('admissions', False))
        request.env['record.request'].sudo().create({'op_admission_id': op_admission_id})
        success_message = 'Solicitud registrada con éxito'
        url = f'/my/requests?success_message={success_message}'
        return url

    @http.route(['/my/documents'], type='http', methods=['GET', 'POST'], auth='public', website=True)
    def document_form_view(self, **kwargs):
        '''
            Update attachment of the partner.
            :param kwargs: Arguments to update the attachment.
            :type kwargs: Dictionary.
            :return: A string that represents the url to be redirected.
            :rtype: str
        '''
        user_id = request.env.uid
        current_user = request.env['res.users'].sudo().browse(user_id)
        values = {
            'page_name': 'document_form_view',
            'partner_id': current_user.partner_id,
            'ir_attachment_ids': current_user.partner_id.ir_attachment_ids
        }
        if request.httprequest.method == 'GET':
            return request.render('isep_record_request.document_form_view', values)
        elif request.httprequest.method == 'POST':
            url = ''
            documents_to_update = [{'document_id': int(key.split('update_document_')[1]), 'file': value}
                                   for key, value in kwargs.items() if key.startswith('update_document_')]
            try:
                for document in documents_to_update:
                    stream = document['file'].stream
                    read_file = stream.read()
                    decoded_file = base64.encodebytes(read_file)
                    if decoded_file:
                        attachment = request.env['ir.attachment'].sudo().browse(document['document_id'])
                        attachment.write({
                            'datas': decoded_file,
                            'name': document['file'].filename,
                            'state': 'on_hold',
                            'public': True,
                            'res_model': 'res.partner',
                            'res_id': current_user.partner_id.id
                        })
                # success_message = 'Documento(s) actualizados con éxito'
                # url = f'/my/requests?success_message={success_message}'
                url = '/my'

            except ValidationError as exception:
                _logger.error(f'******************* ACTUALIZACIÓN DE DOCUMENTO FALLIDA *******************')
                _logger.error(f'***************** Valores de campos incorrectos. Razón: {exception} *****************')

                # error_message = f'Actualización de documento fallida:\nValores de campos incorrectos.\nRazón: {exception}'
                # url = f'/my/requests?error_message={error_message}'
                url = '/my'

            except Exception as exception:
                _logger.error(f'******************* ACTUALIZACIÓN DE DOCUMENTO FALLIDA *******************')
                _logger.error(f'****** El archivo subido no es válido o es demasiado grande. Razón: {exception} ******')

                # error_message = f'Actualización de documento fallida:\nEl archivo subido no es válido o es demasiado '\
                #                 f'grande.\nRazón: {exception}'
                # url = f'/my/requests?error_message={error_message}'
                url = '/my'

            finally:
                return request.redirect(url)
