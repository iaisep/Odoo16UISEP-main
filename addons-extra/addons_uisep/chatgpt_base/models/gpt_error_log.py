# -*- coding: utf-8 -*-
from odoo import fields, models

class GptErrorLog(models.TransientModel):
    _name = 'gpt.error.log'
    _description = 'Registro de Errores de GPT'

    name = fields.Char(string='Nombre del Error', required=True)
    error_message = fields.Text(string='Mensaje de Error', required=True)
    traceback = fields.Text(string='Traceback', help='Detalles técnicos del error')
    function = fields.Char(string='Función', help='Función que generó el error')
    user = fields.Char(string='Usuario')
