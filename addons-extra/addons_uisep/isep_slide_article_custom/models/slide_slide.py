import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    msn_custom = fields.Boolean(
        string='Adherir boton Llamar 24/7 con IA'
    )
