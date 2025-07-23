# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OpAdmissionSepyc(models.Model):
    _inherit = 'op.admission'

    sepyc_program = fields.Boolean(related = 'batch_id.sepyc_program', string = 'Programa Sepyc / Sep')


