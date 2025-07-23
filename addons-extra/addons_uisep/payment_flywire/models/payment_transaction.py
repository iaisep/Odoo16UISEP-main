# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import requests
from werkzeug import urls

from odoo import _, models,fields
from odoo.exceptions import UserError, ValidationError
from odoo import http
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_flywire import const
from odoo.addons.payment_flywire.controllers.main import FlywireController
from werkzeug.urls import url_join

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    flywire_session_url = fields.Char('flywire session url')
    flywire_session_id = fields.Char('flywire session id')
    flywire_type = fields.Selection([('tokenization_and_pay','Tokenization and pay'),('tokenization','Tokenization')], string="Tipo de operación")
    

    def _get_flywire_session_confirm(self):
        self.ensure_one()
        
        
    def _get_flywire_payload_values(self):
        
        recipient_id = self.provider_id._get_flywire_recipient_id(self)
        
        
        base_url = self.provider_id.get_base_url()
        country = self.partner_id.country_id.code or self.company_id.partner_id.country_id.code or "-"
        state_id = self.partner_id.state_id.code or self.company_id.partner_id.state_id.code or "-"
        zip = self.partner_id.zip or self.company_id.partner_id.zip or "-"
        currency_name = self.company_id.currency_id.name
        factor = const.CURRENCIES.get(currency_name).get('unit')        
        amount = int(self.amount*factor)
        

        name_list = self.partner_id.name.split()
        first_name = False
        last_name = False
        if len(name_list) == 1:
            first_name = name_list[0]
            last_name = "-"
        elif len(name_list) == 2:
            first_name = name_list[0]
            last_name = name_list[1]
        elif len(name_list) == 3:
            first_name = name_list[0]
            last_name = f"{name_list[1]} {name_list[2]}"
        elif len(name_list) == 4:
            first_name = f"{name_list[0]} {name_list[1]}"
            last_name = f"{name_list[2]} {name_list[3]}"
        else:
            first_name = f"{name_list[0]} {name_list[1]}"
            last_name = " ".join(name_list[2:])

        
        payload = {
                "type": "one_off",
                "charge_intent": {
                    "mode": "one_off"
                },
                "payor": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "address": self.partner_id.street,
                    "city": self.partner_id.city or "-",
                    "country": country,
                    "state": state_id,
                    "phone": self.partner_id.mobile or self.partner_id.phone,
                    "email": self.partner_id.email,
                    "zip": zip
                },
                "options": {
                    "form": {
                        "locale": "es-ES",
                        "displayPayerInformation": True,
                        "show_payor_information": True,
                        "show_flywire_logo": True
                    }
                },
                "recipient": {
                    "fields": [
                        {
                            "id": "student_id",
                            "value": str(self.partner_id.id).zfill(6)
                        },
                        {
                            "id": "codigo_matricula",
                            "value": str(self.partner_id.id).zfill(6)
                        },
                        {
                            "id": "student_first_name",
                            "value": first_name,
                        },
                        {
                            "id": "student_last_name",
                            "value": last_name,
                        },
                        {
                            "id": "student_email",
                            "value": self.partner_id.email,
                        }
                    ]
                },
                "items": [
                    {
                        "id": "default",
                        "amount": amount, 
                        "description": self.reference
                    }
                ],
                "notifications_url": f"{base_url}payment/flywire/webhook",
                "external_reference": self.reference,
                "recipient_id": recipient_id, #Ejemplo "MFK" 
                "payor_id": str(self.partner_id.id).zfill(6),
                "displayPayerInformation": False,
                "enable_email_notifications": False
            }
        _logger.info("****\n****\n****\n****\n****\n reference id:\n%s", str(self.id))
        return payload

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'flywire':
            return res
        
        base_url = self.provider_id.get_base_url()
        payload = self._get_flywire_payload_values()
        
        _logger.info("**** payload:\n%s", pprint.pformat(payload))
        payment_link_data = self.provider_id._flywire_make_request(payload=payload)
        _logger.info("\n#####\n#####\n#####\nRequest session:\n%s\n#####\n#####\n#####\n", pprint.pformat(payment_link_data))
        # payment_link_data debe devolver ejemplo:
        """{
            "id": "494d2e9d-c0c9-407c-9094-5b3b2a02c00f",
            "expires_in_seconds": 1800,
            "hosted_form": {
                "url": "https://payment-checkout-dev-apache.flywire.cc/v1/form?session_id=494d2e9d-c0c9-407c-9094-5b3b2a02c00f",
                "method": "GET"
            },
            "warnings": []
            }"""

        # Extract the payment link URL and embed it in the redirect form.
        flywire_session_url = payment_link_data['hosted_form']['url']
        rendering_values = {
            'api_url': '%spayment/flywire/sessions/%s/%s' % (base_url,str(self.id),payment_link_data['id']), #(base_url,payment_link_data['id']) # payment_link_data['hosted_form']['url'],
        }
        try:
            self.flywire_session_url = flywire_session_url
            self.flywire_session_id = payment_link_data['id']
        except:
            pass
        _logger.info("**** payload:\n%s", pprint.pformat(payload))
        _logger.info("**** rendering_values:\n%s", pprint.pformat(rendering_values))
        return rendering_values

        
        """payload = {
            'tx_ref': self.reference,
            'amount': self.amount,
            'currency': self.currency_id.name,
            'redirect_url': urls.url_join(base_url, FlywireController._return_url),
            'customer': {
                'email': self.partner_email,
                'name': self.partner_name,
                'phonenumber': self.partner_phone,
            },
            'customizations': {
                'title': self.company_id.name,
                'logo': urls.url_join(base_url, f'web/image/res.company/{self.company_id.id}/logo'),
            },
            'payment_options': const.PAYMENT_METHODS_MAPPING.get(
                self.payment_method_code, self.payment_method_code
            ),
        }"""

