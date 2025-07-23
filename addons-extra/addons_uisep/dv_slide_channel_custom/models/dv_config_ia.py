# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class DvConfigIa(models.Model):
    _name= "dv.config.ia"

    def name_get(self):
        result = []
        for record in self:
            name = 'Configuracion IA gpt'
            result.append((record.id, name))
        return result

    url=fields.Char("Url")
    model_ia=fields.Char("Modelo IA")
    token_id=fields.Char("Token")
    instructions=fields.Text("Instrucciones")
    temp_chat=fields.Float("Temperatura chat")
    auto_score=fields.Boolean("AutoCalificar", help="Activa para Calificar sin intervencion humana")

    


