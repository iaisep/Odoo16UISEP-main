import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)



class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    admission_id = fields.Many2one('op.admission', string="Admisión" , copy=False) 