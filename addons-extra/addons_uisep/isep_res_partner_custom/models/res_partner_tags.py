# -*- coding: utf-8 -*-
from odoo import models, fields
from random import randint


class ResPartnerTags(models.Model):
    _name = 'res.partner.tags'
    _description = 'Partner Tags'

    
    def _get_default_color(self):
        return randint(1, 11)
    
    name = fields.Char(string="Nombre")
    color = fields.Integer(String="Color",  default=_get_default_color )