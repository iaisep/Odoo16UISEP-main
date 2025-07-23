# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time
import base64

import logging
logger = logging.getLogger(__name__)


class HrEmploye(models.Model):
    _inherit = "hr.employee"

    health_partner_id = fields.Many2one('res.partner', string='Partner health',
        help='Eventual third party involved in the payment of the health of the workers.')
    pension_partner_id = fields.Many2one('res.partner', string='Partner pension',
        help='Eventual third party involved in the salary payment pension of the employees.')

