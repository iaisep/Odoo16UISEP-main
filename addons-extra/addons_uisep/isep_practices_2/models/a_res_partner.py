# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime





class ResPartnerCenter(models.Model):
    _inherit = 'res.partner'

    center_id = fields.Many2one(
        'practice.center',
        string="Practice Center",
        help="The practice center associated with this partner."
    )
    #
    official_name = fields.Char(related="center_id.official_name")
    signatory_name = fields.Char(related="center_id.signatory_name")
    #
    tutor = fields.Boolean(string='Is Tutor', default=False)
    center = fields.Boolean(string='Is Center', default=False)
    signatory = fields.Char('Signatory')
