from odoo import models, fields
import json
import logging

class FlywirePayloadLog(models.Model):
    _name = 'flywire.payload.log'
    _description = 'Log de Payloads enviados a Flywire'

    transaction_id = fields.Many2one('payment.transaction', string='Transacción')
    payload_json = fields.Text('Payload JSON')
    date_sent = fields.Datetime('Fecha de Envío', default=fields.Datetime.now)
    error_message = fields.Text('Mensaje de Error')

class PaymentTransactionLogInherit(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code == 'flywire':
            payload = self._get_flywire_payload_values()
            try:
                self.env['flywire.payload.log'].create({
                    'transaction_id': self.id,
                    'payload_json': json.dumps(payload, ensure_ascii=False, indent=2),
                })
            except Exception as e:
                self.env['flywire.payload.log'].create({
                    'transaction_id': self.id,
                    'payload_json': False,
                    'error_message': str(e),
                })
                logging.getLogger(__name__).error(f"Error al guardar el log de Flywire: {e}")
        return res