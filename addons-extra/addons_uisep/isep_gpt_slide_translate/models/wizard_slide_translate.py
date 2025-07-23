# -*- coding: utf-8 -*-
from odoo import fields, models,api,_
from markupsafe import Markup
import json
from psycopg2.extras import Json
from odoo.exceptions import UserError 
from bs4 import BeautifulSoup
import logging
from collections import defaultdict, OrderedDict
_logger = logging.getLogger(__name__)
from lxml import etree as ET, html
from lxml.html import builder as h
from hashlib import sha256
import tiktoken


class WizardSlideTranslate(models.TransientModel):
    _name = 'wizard.slide.translate'
    _description = 'Traduccion de contenido en elearning.'

    name = fields.Char(string='Titulo es_MX' )
    name_pt_br = fields.Char(string='Titulo pt_BR' )
    name_en_us = fields.Char(string='Titulo en_US' )
    # al ser 3 idiomas lo haremos directo en campos html para mejorar la interfaz del usuario
    # translate_line_ids = fields.One2many('wizard.slide.translate.line', 'translate_id', string='Traducciones')
    slide_id = fields.Many2one('slide.slide', string="Contenido", required=True )
    langs_id = fields.Many2many(
        'res.lang',  # Modelo relacionado para idiomas
        string='Idiomas',
        domain="[('code', 'in', ['en_US', 'pt_BR'])]",
    )
    html_es_mx = fields.Html('Español')
    html_pt_br = fields.Html('Portugues')
    html_en_us = fields.Html('Ingles')

    def _count_tokens(self,text):
        """Cuenta los tokens en un texto usando el codificador cl100k_base."""
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


    def _translate_content_dict(self, lang_origin, translate_to, title, content_dict):
        MAX_TOKENS = 1500  # Límite máximo de tokens probando

        integration = self.env['gpt.integration'].search([('code', '=', 'SLIDETRANSLATE')], limit=1)
        if not integration:
            raise UserError("No se encontró la integración con código 'SLIDETRANSLATE'")

        # Convertir el diccionario a una cadena para contar los tokens
        content_str = json.dumps({"title": title, "content_dict": content_dict})
        num_tokens = self._count_tokens(content_str)

        translated_parts = []
        api_interactions = []

        if num_tokens > MAX_TOKENS:
            # Dividir el diccionario en partes más pequeñas si supera el límite de tokens
            current_part = {}
            current_tokens = 0
            for key, value in content_dict.items():
                item_tokens = self._count_tokens(value)
                if current_tokens + item_tokens > MAX_TOKENS:
                    # Traducir la parte actual
                    translated_chunk = self._translate_content_dict_chunk(lang_origin, translate_to, title, current_part)
                    translated_parts.append(translated_chunk)
                    api_interactions.extend(translated_chunk.get("api_interactions", [])) # Agregar interacciones de la parte

                    current_part = {}
                    current_tokens = 0
                current_part[key] = value
                current_tokens += item_tokens

            # Traducir la última parte si existe
            if current_part:
                translated_chunk = self._translate_content_dict_chunk(lang_origin, translate_to, title, current_part)
                translated_parts.append(translated_chunk)
                api_interactions.extend(translated_chunk.get("api_interactions", [])) # Agregar interacciones de la parte

        else:
            # Traducir todo el diccionario si está dentro del límite de tokens
            translated_chunk = self._translate_content_dict_chunk(lang_origin, translate_to, title, content_dict)
            translated_parts.append(translated_chunk)
            api_interactions.extend(translated_chunk.get("api_interactions", [])) # Agregar interacciones



        # Combinar las partes traducidas
        final_title = translated_parts[0]['title'] if translated_parts else title  # Manejo de caso sin partes
        final_content_dict = {}
        for part in translated_parts:
            final_content_dict.update(part['content_dict'])


        return {
            "title": final_title,
            "content_dict": final_content_dict,
            "api_interactions": api_interactions, # Retornar todas las interacciones
        }


    def _translate_content_dict_chunk(self, lang_origin, translate_to, title, content_dict):
        """Función auxiliar para traducir una parte del diccionario."""
        integration = self.env['gpt.integration'].search([('code', '=', 'SLIDETRANSLATE')], limit=1)
        if not integration:
            raise UserError("No se encontró la integración con código 'SLIDETRANSLATE'")

        message = json.dumps({
            "lang_origin": lang_origin,
            "translate_to": translate_to,
            "title": title,
            "content_dict": content_dict
        })
        try:
            data = integration._get_chatgpt_response(integration, message)
            request_data = message
            response_data = data


            if isinstance(data, str):
                try:
                    parsed_data = json.loads(data)
                    # ... (resto del código para manejar la respuesta de la API)
                    if isinstance(parsed_data, dict) and "title" in parsed_data and "content_dict" in parsed_data:

                        return {
                            "title": parsed_data.get("title", title),
                            "content_dict": parsed_data.get("content_dict", {}),
                            "api_interactions": [{'request': request_data, 'response': response_data}], # Lista de interacciones
                        }

                except json.JSONDecodeError:
                    pass
            elif isinstance(data, dict):
                if "title" in data and "content_dict" in data:
                    data['api_interactions'] = [{'request': request_data, 'response': response_data}] # Agregar info de interacción
                    return data

                # ... manejo de errores


            # Si la respuesta no es un diccionario o string válido, retorna un diccionario vacío y registra el error
            _logger.error(f"Tipo de dato no reconocido o formato incorrecto: {type(data)}")
            return {
                "title": title, # Retorna el título original si hay un error.
                "content_dict": {}, # Retorna un diccionario vacío para content_dict en caso de error
                "api_interactions": [], # sin interacciones si no se completa la traducción

            }



        except Exception as e:
            msn = f"Error al obtener respuesta de ChatGPT: {e}"
            _logger.error(msn)
            raise UserError(msn) # Relanzar para detener
    
    

    def _extract_text_and_replace(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        texts = {}
        index = 1
        for element in soup.find_all(string=True):
            text = element.strip()
            if text:
                key = f"%TS{index:04}%" 
                texts[key] = text
                element.replace_with(key)  
                index += 1
        return str(soup), texts  # Retornar el HTML modificado y el diccionario de textos html sin imagenes


    def _rebuild_html(self, translated_texts_str, temp_html):  # Cambiado el nombre del parámetro
        """Reconstruye el HTML con los textos traducidos."""
        translated_texts = translated_texts_str
        try:
            translated_texts = json.loads(translated_texts_str) # Convertir a diccionario
        except:
            pass
        translated_list = translated_texts.get("content_dict", [])
        for key, value in translated_list.items(): # Iterar sobre el diccionario si existe
            temp_html = temp_html.replace(key, value)
        return temp_html
       

    

    
    
    def action_translate(self):
        # ... (resto del código)

        original_html = self.html_es_mx
        if not original_html:
            return

        temp_html, original_texts = self._extract_text_and_replace(original_html) # Obtener HTML temporal y diccionario de textos

        title = self.name

        for lang in self.langs_id:
            if lang.code == 'pt_BR':
                list_html_pt_br_translated = self._translate_content_dict('es_MX', 'pt_BR', title, original_texts)
                self.html_pt_br = self._rebuild_html(list_html_pt_br_translated, temp_html)
                self.name_pt_br = list_html_pt_br_translated.get('title', '')

            elif lang.code == 'en_US':
                list_html_en_us_translated = self._translate_content_dict('es_MX', 'en_US', title, original_texts)
                self.html_en_us = self._rebuild_html(list_html_en_us_translated, temp_html)
                self.name_en_us = list_html_en_us_translated.get('title', '')
        
       
        

    def action_done(self):
        self.ensure_one()
        # self.slide_id.with_context(lang=content.code).sudo().html_content
        # El context funciona para acceder a la traduccion pero no para escribir por eso usamos sql
        # recibe ejemplo:  {"en_US": "<p>hola1</p>", "es_MX": "<p>hola3</p>", "pt_BR": "<p>hola2</p>"}

        html_es_mx = self.html_es_mx or '' #to_translate_es_mx #{sha_es_mx: self.html_es_mx}
        html_pt_br = self.html_pt_br or self.html_es_mx #to_translate_pt_br # {sha_pt_br: self.html_pt_br}
        html_en_us = self.html_en_us or self.html_es_mx  #to_translate_en_us # {sha_en_us: self.html_en_us}

        translations = {            
            'en_US': html_en_us if html_en_us else html_es_mx if html_es_mx else None,
            'es_MX': html_es_mx if html_es_mx else None,
            'pt_BR': html_pt_br if html_pt_br else html_es_mx if html_es_mx else None,
        }

        if not isinstance(translations, dict):
            raise UserError("html_content: El contenido traducido no tiene el formato correcto.")
        html_as_json = Json(translations)     
        self._update_html_content(html_as_json, self.slide_id.id, )


        translations_title = {}
        translations_title['es_MX'] = self.name
        translations_title['pt_BR'] = self.name_pt_br if self.name_pt_br else self.name
        translations_title['en_US'] = self.name_en_us if self.name_en_us else self.name
        if not isinstance(translations_title, dict):
            raise UserError("title: El contenido traducido no tiene el formato correcto.")
        name_as_json = Json(translations_title)

        self._update_name(name_as_json, self.slide_id.id )

        self.slide_id.translate_with_gpt = True


    def _update_html_content(self,json, slide_id):
        query = """
            UPDATE slide_slide
            SET html_content = %s
            WHERE id = %s"""     
        self.env.cr.execute(query, (json, slide_id))
        self.env.cr.commit

    def _update_name(self,json, slide_id):
        query = """
            UPDATE slide_slide
            SET name = %s
            WHERE id = %s;"""        
        self.env.cr.execute(query, (json, slide_id))
        self.env.cr.commit()  

    
