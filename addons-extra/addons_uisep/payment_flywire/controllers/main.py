# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hmac
import logging
import pprint
from pytz import timezone
from werkzeug.exceptions import Forbidden
import requests
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from urllib.parse import urlparse, parse_qs
from werkzeug.urls import url_join
_logger = logging.getLogger(__name__)


class FlywireController(http.Controller):
    _webhook_url = '/payment/flywire/webhook'


        
    @http.route(_webhook_url, type='http', methods=['POST'], auth='public', csrf=False)
    def flywire_webhook(self):

        data = request.get_json_data()
        _logger.info("\n#####\n#####\n#####\nNotification received from Flywire with data:\n%s\n#####\n#####\n#####\n", pprint.pformat(data))

        try:
            event_type = data.get('event_type')
            payment_data = data.get('data', {})
            external_reference = payment_data.get('external_reference')
            status = payment_data.get('status')

            if not external_reference:
                _logger.warning("Notification does not contain an external_reference")
                return request.make_json_response('Missing external_reference', status=400)

            tx_sudo = request.env['payment.transaction'].sudo().search([('reference', '=', external_reference)], limit=1)
            _logger.warning("\n####\n####\n####\nTransaccion encontrada external_reference: %s" % str(tx_sudo))
            if not tx_sudo:
                _logger.warning("No transaction found for reference: %s", external_reference)
                return request.make_json_response('Transaction not found', status=404)

            
            if tx_sudo.state == 'done':
                _logger.warning("\n####\n####\n####\nSe envia status 200 del porque ya esta en done")
                return request.make_json_response('', status=200)
            
            if event_type == 'initiated':
                _logger.info("Payment initiated for transaction: %s", tx_sudo.reference)
                tx_sudo._set_pending()
                return request.make_json_response('', status=200)

            elif event_type == 'processed':
                _logger.info("Payment processed for transaction: %s", tx_sudo.reference)
                tx_sudo._set_pending()
                return request.make_json_response('', status=200)

            elif event_type == 'guaranteed':
                _logger.info("Payment guaranteed for transaction: %s", tx_sudo.reference)
                tx_sudo._set_done()
                
                
                #tx_sudo.env.ref('payment.cron_post_process_payment_tx')._trigger()
                if tx_sudo.tokenize:
                    tx_sudo._get_flywire_session_confirm()
                tx_sudo._reconcile_after_done()
                tx_sudo._execute_callback()       
                return request.make_json_response('', status=200)            

            elif event_type == 'failed':
                _logger.error("Payment failed for transaction: %s", tx_sudo.reference)
                tx_sudo._set_error("Payment failed on Flywire.")
                return request.make_json_response('', status=200)

            elif event_type == 'cancelled':
                _logger.warning("Payment cancelled for transaction: %s", tx_sudo.reference)
                tx_sudo._set_canceled()
                return request.make_json_response('', status=200)

            else:
                _logger.info("Unhandled event type: %s", event_type)

        except Exception as e:
            _logger.exception("Error processing Flywire notification: %s", str(e))
            return request.make_json_response('Error processing notification', status=500)

        # Responder con éxito para que Flywire no reintente
        return request.make_json_response('', status=200)
    
    """    
    {'data': {'amount_from': '116000',
            'amount_to': '116000',
            'country': 'MX',
            'currency_from': 'MXN',
            'currency_to': 'MXN',
            'expiration_date': '2025-01-29T19:17:26Z',
            'external_reference': 'INV/2025/00001-33',
            'fields': {'graduation_year': None,
                        'program_of_study': None,
                        'student_date_of_birth': None,
                        'student_email': 'test@web.com',
                        'student_first_name': 'CLIENTE',
                        'student_id': '000007',
                        'student_last_name': '-',
                        'student_middle_name': None},
            'payment_id': 'MFK473528722',
            'payment_method': {'type': 'card'},
            'status': 'initiated'},
    'event_date': '2025-01-27T19:17:26Z',
    'event_resource': 'payments',
    'event_type': 'initiated'}

    {'data': {'amount_from': '116000',
            'amount_to': '116000',
            'country': 'MX',
            'currency_from': 'MXN',
            'currency_to': 'MXN',
            'expiration_date': '2025-01-29T19:17:26Z',
            'external_reference': 'INV/2025/00001-33',
            'fields': {'graduation_year': None,
                        'program_of_study': None,
                        'student_date_of_birth': None,
                        'student_email': 'test@web.com',
                        'student_first_name': 'CLIENTE',
                        'student_id': '000007',
                        'student_last_name': '-',
                        'student_middle_name': None},
            'payment_id': 'MFK473528722',
            'payment_method': {'brand': 'visa',
                                'card_classification': 'credit',
                                'card_expiration': '03/2030',
                                'last_four_digits': '1111',
                                'type': 'card'},
            'status': 'processed'},
    'event_date': '2025-01-27T19:19:15Z',
    'event_resource': 'charges',
    'event_type': 'processed'}

    {'data': {'amount_from': '116000',
            'amount_to': '116000',
            'country': 'MX',
            'currency_from': 'MXN',
            'currency_to': 'MXN',
            'expiration_date': '2025-01-29T19:17:26Z',
            'external_reference': 'INV/2025/00001-33',
            'fields': {'graduation_year': None,
                        'program_of_study': None,
                        'student_date_of_birth': None,
                        'student_email': 'test@web.com',
                        'student_first_name': 'CLIENTE',
                        'student_id': '000007',
                        'student_last_name': '-',
                        'student_middle_name': None},
            'payment_id': 'MFK473528722',
            'payment_method': {'brand': 'visa',
                                'card_classification': 'credit',
                                'card_expiration': '03/2030',
                                'last_four_digits': '1111',
                                'type': 'card'},
            'status': 'guaranteed'},
    'event_date': '2025-01-27T19:19:15Z',
    'event_resource': 'payments',
    'event_type': 'guaranteed'}


    """
        

        
    @http.route('/payment/flywire/sessions/<string:tx>/status', type='http',  methods=['GET', 'POST'], csrf=False, auth='public', website=True)
    def flywire_session_status(self, tx):      
        tx_sudo = request.env['payment.transaction'].sudo().browse(int(tx))
        tz = tx_sudo.partner_id.tz or 'UTC'
        local_tz = timezone(tz)
        now_utc = tx_sudo.last_state_change
        local_dt = now_utc.astimezone(local_tz)
        date = local_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        name = tx_sudo.partner_name
        ref = tx_sudo.reference
        state = tx_sudo.state
        if not tx_sudo.token_id and tx_sudo.flywire_type == 'tokenization':
            tx_sudo._get_flywire_session_confirm()
        return http.request.render('payment_flywire.flywire_payment_status', {
            'name': name,
            'ref': ref,
            'date': date,
            'state': state,
        })


    @http.route('/payment/flywire/sessions/<string:tx>/<string:session_id>', type='http',  methods=['GET', 'POST'], csrf=False, auth='public', website=True)
    def flywire_session_form(self, tx, session_id):      
        tx_sudo = request.env['payment.transaction'].sudo().browse(int(tx))


        session_url = tx_sudo.flywire_session_url
        
        parsed_url = urlparse(session_url)
        query_params = parse_qs(parsed_url.query)
        extracted_session_id = query_params.get('session_id', [None])[0]

        if extracted_session_id != session_id:
            return request.not_found()

        return http.request.render('payment_flywire.flywire_session_page', {
                'session_url': session_url,
                'tx': int(tx),
            })