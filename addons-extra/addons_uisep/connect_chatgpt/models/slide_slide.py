# -*- coding: utf-8 -*-
from odoo import fields, models,api ,_
from bs4 import BeautifulSoup
import base64
import io
from docx import Document
import openai
import json
import fitz
import tiktoken
import requests

from odoo.exceptions import UserError

class SlideSlide(models.Model):
    _inherit= 'slide.slide'


    embedding_json = fields.Text('Embedding', copy=False)
    preconvertdes = fields.Text(copy=False)
    preconverthtml = fields.Text(copy=False)
    convert = fields.Text(string="Generar Texto", store=True)
    count_tokens = fields.Integer(string='Cantidad tokens', readonly=True)
    embeddings_json = fields.Text(string="Embeddings JSON", store=True)

    create_text= fields.Boolean(copy=False, default=False)
    text_write= fields.Boolean(copy=False,string="Edicion local", default=False)

    @api.model
    def write(self, vals):
        res = super(SlideSlide, self).write(vals)
        if vals.get('description') or vals.get('html_content') or vals.get('slide_category') or vals.get('document_binary_content'):
            self.text_write = False
        return res

    def conver_pre_embedding(self):
        if self.website_published == True:            
            for rec in self:     
                rec.create_text = False 
                if rec.description:
                    soup = BeautifulSoup(rec.description, 'html.parser')
                    paragraphs = soup.find_all(['span']) if soup.find_all(['span']) else soup.find_all(['p'])
                    text_only = ""
                    for p in paragraphs:
                        if p.find('br'):
                            text_only += "\n"
                        else:
                            text_only += p.get_text() + "\n"
                    rec.preconvertdes = text_only.strip()
                if rec.slide_category == 'article' and rec.html_content:                    
                    soup = BeautifulSoup(rec.html_content, 'html.parser')                    
                    tags = soup.find_all(['span']) if soup.find_all(['span']) else soup.find_all(['p'])
                    text_only = ""
                    for p in tags:
                        if p.find('br'):
                            text_only += "\n"
                        else:
                            text_only += p.get_text() + "\n"
                    rec.preconverthtml = text_only.strip()
                self.extract_text_from_attachments()
                self.count_tokens_a()
            return True
    
    def extract_text_from_attachments(self):
        for rec in self:
            all_text = []
            attachment = rec.document_binary_content
            if rec.name:
                all_text.append(str("CURSO DE: "+rec.channel_id.name))
                all_text.append(str("CONTENIDO DE: "+rec.name))
            if rec.preconvertdes:
                all_text.append(rec.preconvertdes)
            if rec.preconverthtml:
                all_text.append(rec.preconverthtml)            
            if rec.slide_category == 'document' and rec.source_type == 'local_file' and attachment:                
                all_text.append(self.extract_text_from_pdf(attachment))            
            rec.convert = "\n".join(all_text)
            
                
    def extract_text_from_pdf(self, data):
        bytes_data = base64.b64decode(data)
        text = ""
        with fitz.open(stream=bytes_data, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    
    def count_tokens_a(self):
        config = self.env['config.openia.embedding'].search([], limit=1)
        maxtoken = config.max_tokens
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        if not self.convert:
            self.count_tokens = 0
            return
        token_count = len(encoding.encode(self.convert))
        self.count_tokens = token_count
        if token_count <= maxtoken:
            self.generate_and_store_embeddings()
            self.create_text == True
        else:
            self.embeddings_json=None
            self.create_text = False
        return token_count
  
####################################################################
    def generate_and_store_embeddings(self):
        config = self.env['config.openia.embedding'].search([], limit=1)
        if not config.api_key:
            raise UserError(_("No se encontró la configuración de OpenIA."))
        text_convert = self.convert
        api_key = config.api_key
        model_gpt = config.model_gpt if config.model_gpt else 'text-embedding-ada-002'      
          
        if text_convert:            
            try:
                openai.api_key = api_key
                response = openai.Embedding.create(input=text_convert, model=model_gpt)
                embedding = response['data'][0]['embedding']
                self.embeddings_json = json.dumps(embedding)
                self.create_text = True
            except Exception as e:
                self.embeddings_json = json.dumps({'error': str(e)})
####################################################################################

    def action_wizard_resume(self):
        view = self.env.ref('connect_chatgpt.resume_gpt_wizard_wizard_form')  
        return {
            'name': 'Generar resumen',
            'type': 'ir.actions.act_window',
            'res_model': 'resume.gpt.wizard',
            'view_mode': 'form',
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_slide_id': self.id,
            }
        }

    def eliminate_use_embeding(self):
        self.create_text = False
        self.text_write = False
        self.count_tokens = 0
        self.convert = None
        self.embedding_json = None

    def action_cron_embedding(self):
        slides = self.search([('active', '=', True), ('create_text', '=', False)])
        for rec in slides:
            if not rec.text_write:
                rec.conver_pre_embedding()
            elif rec.text_write and not rec.embeddings_json: 
                rec.generate_and_store_embeddings()



class SlideChannel(models.Model):
    _inherit= 'slide.channel'

    def execute_convert_pre_embedding(self):
        for channel in self:
            for slide in channel.slide_ids:
                if not slide.create_text:
                    if slide.text_write == False:
                        slide.conver_pre_embedding()
                    elif slide.text_write == True and slide.embeddings_json == None:
                        slide.generate_and_store_embeddings()


class ResumeGptWizard(models.TransientModel):
    _name = 'resume.gpt.wizard'
    _description = 'Generar resumen'

    message = fields.Text(string="Message", default="Crea un resumen detallado y cohesionado que tenga exactamente 8191 tokens de salida, incorporando todos los puntos relevantes, detalles y explicaciones en profundidad.")
    slide_id = fields.Many2one('slide.slide', copy=False, readonly=True)
    convert = fields.Text(string='Texto generado', related='slide_id.convert')
    resume_content = fields.Text(string="Resumen")

    def call_assistant_ia(self): 
        config = self.env['config.openia.embedding'].search([], limit=1)
        token = config.api_key
        url ='https://api.openai.com/v1/chat/completions'
  
        model = 'gpt-4-turbo' # si no se tiene capa de pago usar  gpt-3.5-turbo limite de tokens 16385
        instrucctions = 'You are a creator resumen of text, in spanish'        
        self.resume_content = "" 
        question_today = str( 'Manten los titulos [CURSO DE:] y [CONTENIDO DE:]' + self.message + ': ' + self.convert )   

        messages = [{"role": "system", "content": instrucctions}] if instrucctions else []   
        messages.append({"role": "user", "content": question_today})
        payload = json.dumps({
        "model": model,
        "messages": messages,
        
        })
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
  
        response = requests.request("POST", url, headers=headers, data=payload)
       
        if response.status_code == 200:
            respuesta_json = response.json()
            if respuesta_json.get("choices"):
                first_choice = respuesta_json["choices"][0]
                message = first_choice.get("message", {})
                content = message.get("content", "")
                self.resume_content = content                  
                
                  
            
    def action_confirm(self):
        for rec in self:
            if rec.slide_id:
                self.call_assistant_ia()
                rec.slide_id.write({
                    'convert': rec.resume_content,
                    'text_write' : True })
                self.slide_id.count_tokens_a()
        return True

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}