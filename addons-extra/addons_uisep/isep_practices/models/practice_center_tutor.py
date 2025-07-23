# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeCenterTutor(models.Model):
    _name = 'practice.center.tutor'
    _description = 'PracticeCenterTutor'
    _rec_name = 'tutor_id'

    tutor_id = fields.Many2one('res.partner', string="Tutor", required=True)
    partner_id = fields.Many2one('res.partner')

    @api.onchange('tutor_id')
    def filterPartnerByTutor(self):
        return {'domain': {'tutor_id': [('tutor', '=', True)]}}