# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import _, api, fields, models
_logger = logging.getLogger(__name__)
import pprint
from odoo.addons.payment_flywire import const
import requests
from odoo.exceptions import ValidationError

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
   




     #=== COMPUTE METHODS ===#
    
    
    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'flywire').update({
            'support_express_checkout': True,
            'support_manual_capture': 'full_only',
            'support_refund': 'partial',
            'support_tokenization': True,
        })
    
    
        
    def _get_flywire_payor_token(self,tx):
        payor_id = str(tx.partner_id.id).zfill(6),
        url_base = self.flywire_get_form_action_url()        
        url = url_base + 'payments/v1/payors/%s/payment_methods' % payor_id       
        

        self.ensure_one()

        headers = {
            "Content-Type": "application/json",
            "X-Authentication-Key": self.flywire_api_key
        }
        try:
            
            response = requests.get(url, headers=headers, timeout=10)
           
            try:
                response.raise_for_status()
                try:
                    _logger.exception(
                        "PAYOR payment methods at %s with data:\n%s", url, pprint.pformat(response.json()),
                    )
                except:
                    pass
            except requests.exceptions.HTTPError:
                raise ValidationError("Flywire: " + _(
                    "The communication with the API failed. Flywire gave us the following "
                    "information: '%s'", response.json().get('message', '')
                ))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError(
                "Flywire: " + _("Could not establish the connection to the API.")
            )
        return response.json()
        