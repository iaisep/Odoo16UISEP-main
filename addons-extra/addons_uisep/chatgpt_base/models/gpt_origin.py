# -*- coding: utf-8 -*-
from odoo import fields, models


class GptOrigin(models.Model):
    _name = 'gpt.origin'
    _description = 'GPT Origen'

    name = fields.Char('Nombre')
    api_key = fields.Char(string='API Key', required=True)
    model_ids = fields.One2many('gpt.model', 'gpt_id', string="Modelos")

