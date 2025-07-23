# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import pprint
import requests
from odoo import _, models,fields
from odoo import http
from werkzeug.urls import url_join
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment_flywire import const

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    
    
    
    def _get_flywire_session_confirm(self):
        res = super()._get_flywire_session_confirm()
        try:
            provider = False
            if self.provider_id.code == 'flywire' and self.flywire_session_id:
                provider  = self.provider_id.code
            if not provider:
                _logger.error("\n***\n***\n***\nflywire_confirm_session: Proveedor de Flywire no encontrado o id de sesion invalida.")
                return False

            base_url = self.provider_id.flywire_get_form_action_url()
            url = url_join(base_url, f'/payments/v1/checkout/sessions/{self.flywire_session_id}/confirm')
            _logger.info(f"\n***\n***\n***\nflywire_confirm_session: URL de confirmación: {url}")

            headers = {
                "Content-Type": "application/json",
                "X-Authentication-Key": self.provider_id.flywire_api_key
            }
            _logger.info("\n***\n***\n***\nflywire_confirm_session: Realizando la solicitud POST confirm a Flywire.")
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            _logger.info("flywire_confirm_session: Respuesta de Flywire al confirmar sesión: %s", pprint.pformat(response_data))
            

            mandate = response_data.get('mandate', {})
            payment_method =  response_data.get('payment_method', {})
            _logger.info("FLYWIRE TOKEN: mandante: %s" % mandate)
            _logger.info("FLYWIRE TOKEN: payment_method: %s" % payment_method)
            if mandate and payment_method:
                token = self.env['payment.token'].create({
                    'provider_id': self.provider_id.id,
                    'payment_details': payment_method.get('last_four_digits','9999'),
                    'partner_id': self.partner_id.id,
                    'provider_ref': mandate['id'],
                    'verified': True,
                    'flywire_mandate':mandate['id'],
                    'flywire_token': payment_method['token']
                })
                self.write({
                    'token_id': token,
                    'tokenize': False,
                })
                if self.flywire_type == 'tokenization':
                    self._set_done()
                for order in self.sale_order_ids:
                    if order.is_subscription == True:
                        order.payment_token_id = token
            
            return http.Response(f"Sesión {self.flywire_session_id} confirmada exitosamente", status=200)

        except requests.exceptions.HTTPError as e:
            _logger.error(f"flywire_confirm_session: Error HTTP al confirmar sesión: {e}")
            _logger.error(f"flywire_confirm_session: Contenido de la respuesta: {e.response.content if e.response else 'No disponible'}")
            return http.Response(f"Error al confirmar sesión: {e}", status=500)

        except Exception as e:
            _logger.exception(f"flywire_confirm_session: Error inesperado al confirmar sesión: {e}")
            return http.Response(f"Error inesperado al confirmar sesión: {e}", status=500)
        finally:
            _logger.info(f"flywire_confirm_session: Finalizando la confirmación para session_id: {self.flywire_session_id}")
            
            
    def _get_flywire_payload_values(self):
        """
                {
            "type": "tokenization",
            "charge_intent": {
                "mode": "installment"
            },

            "payor": {
                "first_name": "RECURRING CARD",
                "last_name": "APPROVED",
                "address": "Allen Street",
                "city": "New York",
                "country": "ES",
                "state": "NY",
                "phone": "+34666234567",
                "email": "john.mcenrou@tennis.com",
                "zip": "10002"
            },
                "options": {
                "form": {
                    "action_button": "save",
                    "show_flywire_logo": true,
                    "locale": "en"
                }
            },
            "schema": "cards",
            "payor_id": "MCAWESOME",
            "notifications_url": "https://webhook.site/6ff82c43-94f3-4651-b45d-80c9e02d97de",
            "external_reference": "testgoo",
            "recipient_id": "DHN"
        }   
        """
        res = super(PaymentTransaction, self)._get_flywire_payload_values()
        if self.amount > 0:
            for order in self.sale_order_ids:
                if order.is_subscription == True:
                    self.tokenize = True
                    self.flywire_type = 'tokenization_and_pay'
                    res['type'] = "tokenization_and_pay"
                    res['charge_intent'] = {"mode": "unscheduled"}
                    res['schema'] = "cards"
                    break
        else:
            self.tokenize = True
            self.flywire_type = 'tokenization'
            res['type'] = "tokenization"
            res['charge_intent'] = {"mode": "unscheduled"}
            res['schema'] = "cards"
                 
        _logger.info("****update payload:\n%s", pprint.pformat(res))
        
        return res
    
    
        
    def _send_payment_request(self):
        
        super()._send_payment_request()
        if self.provider_code != 'flywire':
            return

        if not self.token_id:
            raise UserError("flywire: " + _("The transaction is not linked to a token."))

        # Make the payment request to flywire
        payment_intent = self._flywire_create_payment_intent()
        _logger.info(
            "payment request response for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(payment_intent)
        )
        if not payment_intent:  # The PI might be missing if Stripe failed to create it.
            return  # There is nothing to process; the transaction is in error at this point.

        # Handle the payment request response
        notification_data = {'reference': self.reference}
        self._handle_notification_data('flywire', notification_data)
    
    def _flywire_create_payment_intent(self):
        """ Create and return a PaymentIntent.

        Note: self.ensure_one()

        :return: The Payment Intent
        :rtype: dict
        """
        if not self.token_id:
            return
        response = self.provider_id._flywire_make_request(
            payload=self._flywire_prepare_payment_intent_payload(),
            url='/payments/v1/payments/charge'
        )
                
        if 'error' not in response:
            payment_intent = response
        else:
            error_msg = response['error'].get('message')
            _logger.warning(
                "The creation of the payment intent failed.\n"
                "Flywire gave us the following info about the problem:\n'%s'", error_msg
            )
            self._set_error("Flywire: " + _(
                "The communication with the API failed.\n"
                "Flywire gave us the following info about the problem:\n'%s'", error_msg
            ))
            payment_intent = response['error'].get('payment_intent')

        return payment_intent 

    def _flywire_prepare_payment_intent_payload(self):
        currency_name = self.company_id.currency_id.name
        factor = const.CURRENCIES.get(currency_name).get('unit')        
        amount = int(self.amount*factor)
        base_url = self.provider_id.get_base_url()
        payload = {
            "charge_intent": {
                "mode": "installment"
            },
            "mandate_id": self.token_id.flywire_mandate,
            "payment_method_token": self.token_id.flywire_token,
            "payor_id": str(self.partner_id.id).zfill(6),
            "recipient": {
                "id": self.provider_id.sudo()._get_flywire_recipient_id(self),
                "fields": [
                        {
                            "id": "student_id",
                            "value": str(self.partner_id.id).zfill(6)
                        },
                        {
                            "id": "student_first_name",
                            "value": self.partner_id.name,
                        },
                        {
                            "id": "student_last_name",
                            "value": self.partner_id.name,
                        },
                        {
                            "id": "student_email",
                            "value": self.partner_id.email,
                        }
                    ],          
            },
            "items": [
                {
                    "id": "default",
                    "amount": amount,
                    "description": self.reference
                }
            ],
            "metadata": {
                "Internal-ID": str(self.partner_id.id).zfill(6),
                "Int-Comment": self.partner_id.name,
            },
            "notifications_url": f"{base_url}/payment/flywire/charge/webhook",
            "external_reference": self.reference,
        }
        
        return payload
    
    