# -*- coding: utf-8 -*-

import uuid
from odoo import models, fields, api, _


class res_partner_extends(models.Model):
    _inherit = 'res.partner'

    card_ids = fields.One2many(
        'res.card', 'partner_id', string='Tarjetas')



