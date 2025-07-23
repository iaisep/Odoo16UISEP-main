# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools import ValidationError
import openai
import traceback
import pkg_resources
import requests
import json
from odoo.exceptions import UserError

class GptIntegration(models.Model):
    _name = 'gpt.integration'
    _description = "Integracion con inteligencia artificial"

    # Pensado para guardar credenciales de API, Chatgpt, Gemini etc.
    name = fields.Many2one('gpt.origin', string='GPT')
    description = fields.Char(string='Descripción', placeholder="Ejemplo: Se encarga de responder los correos" , required=True)    
    model_id = fields.Many2one('gpt.model', string='Modelo')
    code = fields.Char(string='Codigo Interno', placeholder="Ejemplo: CHATGPT123", help="Es un valor unico, Se usa para referenciar en el codigo." ,required=True)
    prompt = fields.Text(string='Instrucciones para la IA (prompt)', placeholder="Instrucciones para la IA" , required=True)
    active = fields.Boolean(String="Activo", default=True)
    

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError("El Código Interno debe ser único.")

    
    def _get_chatgpt_response(self, integration, message):
        api_key = integration.name.api_key
        model = integration.model_id.name
        prompt = integration.prompt

        try:
            # Obtener la versión de la librería openai
            openai_version = pkg_resources.get_distribution("openai").version
            major_version = int(openai_version.split('.')[0])

            if major_version >= 1:  # Versiones 1.x.x o superiores
                client = openai.OpenAI(api_key=api_key)
                if model.strip() in ('text-embedding-3-small','text-embedding-3-large','text-embedding-ada-002'):
                    response = client.embeddings.create(input=message, model=model)
                    return response.data[0].embedding
                else:
                    response = client.chat.completions.create(
                    messages=[
                            {"role": "system", "content": prompt},  # Instrucciones generales para el modelo
                            {"role": "user", "content": message }  # La pregunta del usuario
                        ],
                        model=model,
                        temperature=0.6,
                        max_tokens=3000,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0,
                        user=self.env.user.name
                    )
                    res = response.choices[0].message.content
                    return res

            else:  # Versiones anteriores a la 1.0.0 (como 0.28)
                url = "https://api.openai.com/v1/chat/completions"
                messages = [{"role": "system", "content": prompt}, {"role": "user", "content": message}] if prompt else [{"role": "user", "content": message}]
                
                payload = json.dumps({
                    "model": model,
                    "messages": messages,
                    "temperature": 0.6,
                    "max_tokens": 3000 
                    })

                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code != 200:
                    raise Exception(f"Error en la API de OpenAI: {response.status_code} - {response.text}")
                
                response_data = response.json()    
                first_choice = response_data["choices"][0]
                message = first_choice.get("message", {})
                content = message.get("content", "")                
                return content


        except Exception as e:
            error_details = {
                'name': 'GPT Error',
                'error_message': str(e),
                'traceback': traceback.format_exc(),
                'function': '_get_chatgpt_response'
            }
            return self.env['gpt.error.log'].sudo().create(error_details)
