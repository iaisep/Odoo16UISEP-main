from odoo import api, fields, models, Command
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    
    def recurring_payment_invoice(self):
        self.ensure_one()
        for record in self:
            inv = record
            record.env['payment.transaction']._force_recurring_payment_invoice(inv,100)
        