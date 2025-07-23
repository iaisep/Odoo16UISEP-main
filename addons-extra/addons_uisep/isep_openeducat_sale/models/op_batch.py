import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpCourse(models.Model):
    _inherit = 'op.batch'    

    date_limit = fields.Date("Fecha Limite de inscripción")
    