from odoo import models, fields, api


class CustomopSession(models.Model):
    
    _inherit = 'op.session'

    time_url_metting=fields.Char(string='URL clase virtual')

    time_url_recoding=fields.Char(string='URL grabacion')

   




