from odoo import models, fields

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    flywire_recipient_id = fields.Many2one(
        'payment.flywire.recipient', 
        string="Flywire Recipient",
        help="Recipient ID for Flywire payments"
    )