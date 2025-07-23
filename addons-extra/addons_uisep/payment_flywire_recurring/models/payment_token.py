# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    
    flywire_mandate = fields.Char(string="Flywire Mandate")
    flywire_token = fields.Char(string="Flywire Token")
