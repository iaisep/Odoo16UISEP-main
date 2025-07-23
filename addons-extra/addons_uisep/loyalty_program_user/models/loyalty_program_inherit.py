
from odoo import models, fields

class LoyaltyProgramInherit(models.Model):
    _inherit = 'loyalty.program'

    user_id = fields.Many2one('res.users', string='Responsable')
