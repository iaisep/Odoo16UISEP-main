# -*- coding: utf-8 -*-
from odoo import fields, models


class GptTest(models.Model):
    _name = 'gpt.test'
    _description = 'Registro de test GPT'

    name = fields.Many2one('gpt.integration', string='Integración' , required=True)
    mesasage = fields.Text(string='Mensaje', required=True)
    response = fields.Text(string='Respuesta')


    def integration_test(self):
        integration = self.name # En otros modelos obtenerlo desde self.env['gpt.integration'].search([('code','=', self.name.code)])
        message=self.mesasage
        res = integration._get_chatgpt_response(integration, message )
        self.response=res

