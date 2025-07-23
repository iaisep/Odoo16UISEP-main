from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    flywire_recipient_id = fields.Many2one(
        'payment.flywire.recipient', 
        string="Flywire Recipient",
        help="Recipient ID for Flywire payments"
    )