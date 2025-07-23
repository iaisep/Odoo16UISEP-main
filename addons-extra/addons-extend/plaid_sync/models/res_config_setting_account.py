from odoo import fields, models, api, _

class Company(models.Model):
    _inherit = "res.company"

    plaid_client = fields.Char(string="Plaid Client ID", readonly=False)
    plaid_secret = fields.Char(string="Plaid Secret", readonly=False)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    plaid_client = fields.Char(string="Plaid Client ID", readonly=False, related='company_id.plaid_client')
    plaid_secret = fields.Char(string="Plaid Secret", readonly=False, related='company_id.plaid_secret')
