
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # anulamos las notificaiones por default de correos al fallar o al tener exito una transacción
    # En el caso de flywire las vamos a manejar segun la informacion que se procesa en el webhook
    
    def _handle_subscription_payment_failure(self, invoice, transaction, email_context):
        if transaction.provider_code == 'flywire':
            return
        res = super(SaleOrder, self)._handle_subscription_payment_failure(invoice,transaction,email_context)
        return res
    
    def _subscription_post_success_payment(self, invoice, transaction):
        if transaction.provider_code == 'flywire':
            return
        res = super(SaleOrder, self)._subscription_post_success_payment(invoice, transaction)
        return res
    
    