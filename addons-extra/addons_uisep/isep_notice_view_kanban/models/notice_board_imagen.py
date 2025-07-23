from odoo import models, fields
import secrets
import logging  
_logger = logging.getLogger(__name__)


class OpNoticeBoardImagen(models.Model):

    _inherit = 'op.notice'

    preview=fields.Binary(string="Imagen")

class OpNoticeBoardCircularImagen(models.Model):

    _inherit = 'op.circular'

    preview=fields.Binary(string="Imagen")