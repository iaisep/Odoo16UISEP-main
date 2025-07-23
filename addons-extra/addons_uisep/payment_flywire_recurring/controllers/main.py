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
    _webhook_url = '/payment/flywire/charge/webhook'


        
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
            if tx_sudo.state == 'done':
                _logger.warning("\n####\n####\n####\nSe envia status 200 del porque ya esta en done")
                return request.make_json_response('', status=200)
            
            _logger.warning("\n####\n####\n####\nTransaccion encontrada external_reference: %s" % str(tx_sudo))
            if not tx_sudo:
                _logger.warning("No transaction found for reference: %s", external_reference)
                return request.make_json_response('Transaction not found', status=404)

            if event_type == 'initiated':
                _logger.info("Payment initiated for transaction: %s", tx_sudo.reference)
                tx_sudo._set_pending()
                _logger.warning("\n####\n####\n####\nSe envia status 200 del stado initiated")
                return request.make_json_response('', status=200)

            elif event_type == 'processed':
                _logger.info("Payment processed for transaction: %s", tx_sudo.reference)
                tx_sudo._set_pending()
                _logger.warning("\n####\n####\n####\nSe envia status 200 del stado processed")
                return request.make_json_response('', status=200)

            elif event_type == 'guaranteed':
                _logger.info("Payment guaranteed for transaction: %s", tx_sudo.reference)        
                tx_sudo._set_done()
                try:
                    tx_sudo._reconcile_after_done()
                except:
                    pass
                
                try:
                    tx_sudo._execute_callback()
                except:
                    pass

                # tx_sudo.env.ref('payment.cron_post_process_payment_tx')._trigger()   
                _logger.warning("\n####\n####\n####\nSe envia status 200 del stado guaranteed")                 
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
    
   