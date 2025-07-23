# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import requests
from werkzeug.urls import url_join
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.payment_flywire import const
from odoo.http import request
_logger = logging.getLogger(__name__)

class PaymentFlywireRecipient(models.Model):
    _name = 'payment.flywire.recipient'

    recipient_id = fields.Char(string="Recipient ID", required=True)
    external_code = fields.Char(string="External code")
    name = fields.Char(string="Name")
    country = fields.Char(string="Country")
    state = fields.Char(string="State")
    provider_id = fields.Many2one('payment.provider', ondelete="cascade")


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('flywire', "Flywire")], ondelete={'flywire': 'set default'}
    )
    flywire_shared_key = fields.Char(
        string="Flywire Shared Key",
        help="The key solely used to identify the account with Flywire.",
        required_if_provider='flywire',
        default="Flywire Shared Key",
    )
    flywire_api_key = fields.Char(
        string="Flywire API Key",
        required_if_provider='flywire',
        default="Flywire API Key",
    )    
    flywire_frontend_api_key = fields.Char(
        string="Flywire frontend API key",
        required_if_provider='flywire',
        default="Flywire frontend API key",
    )
    flywire_default_recipient_id = fields.Many2one('payment.flywire.recipient', string="Default Recipient")
    flywire_recipient_ids = fields.One2many('payment.flywire.recipient', 'provider_id', string='Recipients')
    flywire_recipient_priority = fields.Selection(
        selection=[('in_currency', "Recipient in currency"),('in_product', "Recipient in product"),('default', "Default Recipient")], string="Priority recipient",
        default="default" 
    )
   
    def _get_flywire_recipient_id(self,tx):
        recipient_id = False
        flywire_recipient_priority = tx.provider_id.flywire_recipient_priority
        if flywire_recipient_priority != 'default':
            for order in tx.sale_order_ids:
                if flywire_recipient_priority == 'in_currency':
                    if order.currency_id.flywire_recipient_id:
                        recipient_id = order.currency_id.flywire_recipient_id.recipient_id
                        break
                if flywire_recipient_priority == 'in_product':
                    for ln in sorted(order.order_line, key=lambda x: x.price_total, reverse=True):                
                        if ln.product_template_id.flywire_recipient_id:
                            recipient_id = ln.product_template_id.flywire_recipient_id.recipient_id
                            break
                        
            if not recipient_id:
                for inv in tx.invoice_ids:
                    if flywire_recipient_priority == 'in_currency':
                        if inv.currency_id.flywire_recipient_id:
                            recipient_id = inv.currency_id.flywire_recipient_id.recipient_id
                            break                
                    if flywire_recipient_priority == 'in_product':
                        for ln in sorted(inv.invoice_line_ids, key=lambda x: x.price_total, reverse=True):                    
                            if ln.product_id.flywire_recipient_id:
                                recipient_id = ln.product_id.flywire_recipient_id.recipient_id
                                break
        
        if not recipient_id:
            recipient_id = tx.provider_id.flywire_default_recipient_id.recipient_id
        _logger.info('#################################\nrecipient_id: %s\n#################################' % str(recipient_id))
        if not recipient_id:
            raise ValidationError(
                "Flywire: " + "Recipiente no configurado."
            )            
        return recipient_id
    
    def action_flywire_get_recipients(self):
        """ Obtiene los destinatarios de Flywire y los registra en el modelo payment.flywire.recipient. """
        self.ensure_one()
        
        url = self.flywire_get_form_action_url() + '/payments/v1/recipients?per_page=20'
        
        headers = {
            "Content-Type": "application/json",
            "X-Authentication-Key": self.flywire_api_key
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'recipients' in response_data:
                recipients = response_data['recipients']
                
                recipient_records = []
                for recipient_data in recipients:
                    recipient_record = self.env['payment.flywire.recipient'].create({
                        'recipient_id': recipient_data.get('id'),
                        'external_code': recipient_data.get('external_code', ''),
                        'name': recipient_data.get('name', ''),
                        'country': recipient_data.get('country', ''),
                        'state': recipient_data.get('state', ''),
                        'provider_id': self.id
                    })
                    
                    recipient_records.append(recipient_record)
            
                if recipient_records:
                    self.flywire_default_recipient_id = recipient_records[0].id
                
                
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Advertencia',
                        'message': 'No se encontraron destinatarios en la respuesta de Flywire.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }
        
        except requests.exceptions.HTTPError as e:
            # Manejar errores HTTP
            error_message = f"Flywire: Error en la comunicación con la API. Detalles: {e}"
            _logger.error(error_message)
            raise ValidationError(error_message)
        
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            # Manejar errores de conexión o timeout
            error_message = "Flywire: No se pudo establecer la conexión con la API."
            _logger.error(error_message)
            raise ValidationError(error_message)
        
        except Exception as e:
            # Manejar cualquier otro error inesperado
            error_message = f"Flywire: Error inesperado al obtener los destinatarios. Detalles: {e}"
            _logger.error(error_message)
            raise ValidationError(error_message)
                

    # === BUSINESS METHODS ===#


    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'flywire':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies
    
    
    def flywire_get_form_action_url(self):
        self.ensure_one()
        # 4111 1111 1111 1111	03/30	737
        if self.state == 'enabled':
            #url = 'https://api-platform-sandbox.flywire.com' # return 'https://api-platform.flywire.com'
            url = 'https://api-platform.flywire.com'
            _logger.info('**** Enpoint: %s' % url)
            return url 
        else:
            url = 'https://api-platform-sandbox.flywire.com'
            _logger.info('**** Enpoint: %s' % url)
            return url
            

    def _flywire_make_request(self, payload=None, url='/payments/v1/checkout/sessions', method='POST'):
        """ Make a request to Flywire API at the specified endpoint.

        Note: self.ensure_one()
        :param str endpoint: The endpoint to be reached by the request.
        :param dict payload: The payload of the request.
        :param str method: The HTTP method of the request.
        :return The JSON-formatted content of the response.
        :rtype: dict
        :raise ValidationError: If an HTTP error occurs.
        """
        path = request.httprequest.path
        
        _logger.info("\n###path###\n###\nFlywire path: %s",  str(path) ) 
        
        self.ensure_one()

        url = self.flywire_get_form_action_url() + url
        headers = {
            "Content-Type": "application/json",
            "X-Authentication-Key": self.flywire_api_key
        }
        #headers = {'Authorization': f'Bearer {self.flywire_api_key}'}
        _logger.info("Flywire Request Data: %s",  pprint.pformat(payload) )  # Imprime los datos que se enviarán
        _logger.info("Flywire Endpoint: %s", url) # Imprime la URL a la que se enviará la solicitud
        try:
            if method == 'GET':
                response = requests.get(url, params=payload, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                _logger.error("Flywire API Error: %s", e)  # Imprime el error HTTP completo
                _logger.exception(
                    "Invalid API request at %s with data:\n%s", url, pprint.pformat(payload),
                )
                raise ValidationError("Flywire: " + _(
                    "The communication with the API failed. Flywire gave us the following "
                    "information: '%s'", response.json()
                ))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError(
                "Flywire: " + _("Could not establish the connection to the API.")
            )
        return response.json()

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'flywire':
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES

    
