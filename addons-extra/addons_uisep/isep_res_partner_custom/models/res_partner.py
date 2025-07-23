# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_tag = fields.Char(string='No usar')
    custom_tag_id = fields.Many2many('res.partner.tags',string="Etiquetas")