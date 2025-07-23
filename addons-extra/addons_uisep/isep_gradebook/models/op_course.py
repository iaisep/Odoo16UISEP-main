
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)

class OpCourse(models.Model):
    _inherit = 'op.course'

    gradebook_id = fields.Many2one('app.gradebook', string='Calificaciones template' )

    