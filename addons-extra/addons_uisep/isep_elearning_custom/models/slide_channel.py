import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    op_subject_ids = fields.One2many('op.subject','slide_channel_id', 'Asignaturas asociadas')

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    slide_category = fields.Selection(selection_add=[
        ('certification', 'Asignacion/Evaluación/Certification')
    ], ondelete={'certification': 'set default'})
    slide_type = fields.Selection(selection_add=[
        ('certification', 'Asignacion/Evaluación/Certification')
    ], ondelete={'certification': 'set null'})
