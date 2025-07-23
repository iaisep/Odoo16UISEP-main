# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    date_start_tarjet = fields.Datetime(string='Fecha inicial de Envio de link de registro de tarjeta', config_parameter='date_start_tarjet')
    # date_end_tarjet = fields.Datetime(string='Fecha final de Envio de link de registro de tarjeta', config_parameter='date_end_tarjet')
