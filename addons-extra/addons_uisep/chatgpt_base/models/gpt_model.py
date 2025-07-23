# -*- coding: utf-8 -*-
from odoo import fields, models


class GptModel(models.Model):
    _name = 'gpt.model'
    _description = 'Registro de modelos GPT'

    name = fields.Char('Modelos', required=True)
    description = fields.Char('Descripción', required=True)
    max_input = fields.Integer('Limite Tokens', required=True)
    gpt_id = fields.Many2one('gpt.origin', string='GPT')
    
