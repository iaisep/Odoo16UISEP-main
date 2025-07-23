# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class ResPartnerCenter(models.Model):
    _inherit = 'op.course'
    center_id = fields.Many2one(
        'practice.center',
        string="Practice Center",
        help="The practice center associated with this course."
    )
