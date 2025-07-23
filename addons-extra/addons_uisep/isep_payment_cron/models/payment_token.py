import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PaymentToken(models.Model):
    _inherit = 'payment.token'
    
    
    def _build_display_name(self, *args, max_length=34, should_pad=True, **kwargs):
        res = super(PaymentToken, self)._build_display_name(*args, max_length=34, should_pad=True, **kwargs)   
        display_name = '%s - %s' % ( str(self.provider_code) , str(res) )
        
        return display_name
    