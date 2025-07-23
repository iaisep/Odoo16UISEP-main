from odoo import http
import hmac
import hashlib
import base64
import json
import requests
from odoo.http import request
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class Main(http.Controller):
    _url_webhook_recurring = '/payment/flywire/webhook/notification'


    def _validate_flywire_notification(self, raw_body, flywire_digest, shared_secret):
        # Crea el HMAC-SHA256 del cuerpo de la notificación usando el Shared Secret
        hmac_obj = hmac.new(shared_secret.encode('utf-8'), raw_body, hashlib.sha256)
        calculated_digest = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        _logger.info("calculated_digest"*100, calculated_digest)
        _logger.info("flywire_digest"*100, flywire_digest)
        # Compara el digest calculado con el digest recibido en el encabezado
        return hmac.compare_digest(calculated_digest, flywire_digest)



    @http.route(_url_webhook_recurring, type='json', auth='public', methods=['POST'], csrf=False)
    def flywire_webhook(self):
        try:
            # Obtener el cuerpo de la notificación sin procesar
            raw_body = request.httprequest.data
            body = raw_body.decode('utf-8')
            flywire_digest = request.httprequest.headers.get('X-Flywire-Digest')
            session_flywire = request.env['data.flywire'].sudo().search(
            [('active', '=', True)], limit=1)
            # shared_secret = '1FA54436E5DCFA1FE0EDCA04C9E7BE94EDAE524495C38877D1AE32FE7C26DEAA'  # Obtén tu shared secret de la configuración
            shared_secret = session_flywire.shared_secret

            # Validar la notificación
            _logger.info("info"*100, raw_body, flywire_digest, shared_secret)
            if not self._validate_flywire_notification(raw_body, flywire_digest, shared_secret):
                return json.dumps({'status': 'error', 'message': 'Invalid notification'})

            # payload = request.jsonrequest
            payload = json.loads(body)
            if not payload:
                return json.dumps({'status': 'error', 'message': 'No payload received'})

            data = payload.get('data', {})
            payment_method = data.get('payment_method', {})
            fields = data.get('fields', {})

            def convert_date(date_str):
                if date_str:
                    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
                return False

            expiration_date = convert_date(data.get('expiration_date'))

            # Buscar el registro existente por payment_id
            payment_id = data.get('payment_id')
            existing_record = request.env['flywire.notification'].sudo().search([('payment_id', '=', payment_id)], limit=1)

            values = {
                'payment_id': payment_id,
                'amount_from': data.get('amount_from'),
                'currency_from': data.get('currency_from'),
                'amount_to': data.get('amount_to'),
                'currency_to': data.get('currency_to'),
                'status': data.get('status'),
                'expiration_date': expiration_date,
                'external_reference': data.get('external_reference'),
                'country': data.get('country'),
                'card_type': payment_method.get('type'),
                'card_brand': payment_method.get('brand'),
                'card_classification': payment_method.get('card_classification'),
                'card_expiration': payment_method.get('card_expiration'),
                'last_four_digits': payment_method.get('last_four_digits'),
                'student_id': fields.get('student_id'),
                'student_email': fields.get('student_email'),
                'student_first_name': fields.get('student_first_name'),
                'student_last_name': fields.get('student_last_name'),
                'enrollment_id': fields.get('enrollment_id'),
                'payment_type': fields.get('payment_type'),
                'payment_type_other': fields.get('payment_type_other'),
            }


            if existing_record:
                # Actualizar el registro existente
                existing_record.sudo().write(values)
            else:
                # Crear un nuevo registro
                request.env['flywire.notification'].sudo().create(values)

            return json.dumps({'status': 'success'})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    



    @http.route('/payments/v1/checkout/sessions/<int:invoice_id>', type='http', auth='public', website=True)
    def flywire_payment(self, invoice_id):
        invoice = request.env['account.move'].sudo().browse(invoice_id)
        if not invoice:
            return request.render('isep_payment_recurring.session_flywire_error')

        success, result = invoice.create_flywire_session()
        if success:
            return request.render('isep_payment_recurring.session_flywire', {'hosted_form_url': result, 'invoice_id': invoice_id})
        else:
            return request.render('isep_payment_recurring.session_flywire_error', {'error_message': result})


        
    @http.route('/flywire/confirm_checkout_session', type='json', auth='public')
    def confirm_checkout_session(self, **kwargs):
        confirm_url = kwargs.get('confirm_url')
        if not confirm_url:
            _logger.error('Missing confirm_url')
            return {'status': 'error', 'message': 'Missing confirm_url'}

        invoice_id = kwargs.get('invoice_id')
        if not invoice_id:
            _logger.error('Missing invoice_id')
            return {'status': 'error', 'message': 'Missing invoice_id'}
        invoice = request.env['account.move'].sudo().browse(invoice_id)
        if not invoice:
            _logger.error('Missing invoice')
            return {'status': 'error', 'message': 'Invoice not found'}

        result = invoice.confirm_flywire_session(confirm_url)
        _logger.info('Confirm session result: %s', result)
        return result



    @http.route('/flywire/create_payment', type='json', auth='public')
    def create_payment(self, **kwargs):
        payment_method = kwargs.get('payment_method')
        mandate = kwargs.get('mandate')
        invoice_id = kwargs.get('invoice_id')
        _logger.info("create_payment"*20, payment_method, mandate, invoice_id)

        if not payment_method or not mandate or not invoice_id:
            return {'status': 'error', 'message': 'Missing required parameters'}

        invoice = request.env['account.move'].sudo().browse(invoice_id)
        if not invoice:
            return {'status': 'error', 'message': 'Invoice not found'}

        result = invoice.create_flywire_payment(payment_method, mandate)
        return result