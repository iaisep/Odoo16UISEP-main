import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpSubject(models.Model):
    _inherit = 'op.subject'

    slide_channel_id = fields.Many2one('slide.channel', string="Asignatura en Elearning")
