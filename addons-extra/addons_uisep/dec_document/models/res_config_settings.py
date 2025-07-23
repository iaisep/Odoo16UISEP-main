# -*- coding: utf-8 -*-

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    dec_responsable_id = fields.Many2one('res.partner', string="Responsable DEC", help="Partner responsable en lod certificados DEC")

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dec_responsable_id = fields.Many2one('res.partner', related="company_id.dec_responsable_id", readonly= False, string="Responsable DEC", help="Partner responsable en lod certificados DEC")





