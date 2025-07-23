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
from odoo.exceptions import UserError


class ArticleEmbedding(models.Model):
    _name = 'article.embedding'

    name = fields.Char(string='Titulo', readonly=True)
    article_id = fields.Many2one('knowledge.article',string='Articulo', readonly=True)      
    count_tokens = fields.Integer(string='Cantidad tokens', readonly=True)

    body = fields.Text(string='contenido')
    attanchments_ids=fields.Many2many('ir.attachment', string="Adjuntos de conocimiento",relation='article_embedding_knowledge_rel',column1='embedding_id', column2='attachment_id',)
    convert = fields.Text(string="Convertido", store=True)
    embeddings_json = fields.Text(string="Embeddings JSON", store=True)    

    def extract_text_from_attachments(self):
        for record in self:
            all_text = []
            if record.body:
                all_text.append(record.body)            
            for attachment in record.attanchments_ids:                
                if attachment.mimetype == 'application/pdf':
                    all_text.append(self.extract_text_from_pdf(attachment.datas))
                elif attachment.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    all_text.append(self.extract_text_from_docx(attachment.datas))
            record.convert = "\n".join(all_text)

    def extract_text_from_pdf(self, data):
        bytes_data = base64.b64decode(data)
        text = ""
        with fitz.open(stream=bytes_data, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text


        
    def extract_text_from_docx(self, data):
        bytes_data = base64.b64decode(data)
        doc = Document(io.BytesIO(bytes_data))
        return "\n".join([para.text for para in doc.paragraphs])   
    
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
            except Exception as e:
                self.embeddings_json = json.dumps({'error': str(e)})
        

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
        else:
            raise UserError(_(
            "Registro no creado debido a exceso de tokens: {tokens}. "
            "Rebaje la cantidad de texto que desea generar para entrar al rango de tokens: {max_tokens}."
            ).format(tokens=token_count, max_tokens=maxtoken))
        return token_count



class ConfigOpeniaEmbedding(models.Model):
    _name = 'config.openia.embedding'
    _description = "Configuración embeddings OpenIA"

    def name_get(self):
        result = []
        for record in self:
            name = 'Configuración embeddings OpenIA'
            result.append((record.id, name))
        return result

    name = fields.Char(string="Nombre")
    api_key = fields.Char(string="Token",help='Coloque aca el token api que proporciona OpenIA', store=True)
    model_gpt = fields.Char(string="Modelo IA",help='Tipo de modelo de inteligencia que se utilizara para realizar los embeddings', default='text-embedding-ada-002', store=True)
    max_tokens = fields.Integer(string="Maximo tokens", help='Maximo de tokens permitindos por OpenIA', default="8191", store=True)
    webdoc_embeding= fields.Char(string="Documentación", default='https://platform.openai.com/docs/guides/embeddings/embedding-models')
    

class Article(models.Model):
    _inherit= 'knowledge.article'

    def create_embedding(self):
        for rec in self:
            existing_embedding = self.env['article.embedding'].search([('article_id', '=', rec.id)], limit=1)
            soup = BeautifulSoup(rec.body, 'html.parser')
            paragraphs = soup.find_all('p')
            text_only = ""

            for p in paragraphs:
                if p.find('br'):
                    text_only += "\n"
                else:
                    text_only += p.get_text() + "\n"

            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'knowledge.article'),
                ('res_id', '=', rec.id)
            ])

            if existing_embedding:
                existing_embedding.write({
                    'body': text_only.strip(),
                    'attanchments_ids': [(6, 0, attachments.ids)] if attachments else False,
                })
                existing_embedding.extract_text_from_attachments()
                
                if not existing_embedding.count_tokens_a():
                    raise UserError(_("Registro no actualizado debido a exceso de tokens."))
            else:
                new_embedding = self.env['article.embedding'].create({
                    'name': rec.name,
                    'article_id': rec.id,
                    'body': text_only.strip(),
                    'attanchments_ids': [(6, 0, attachments.ids)] if attachments else False,
                })
                new_embedding.extract_text_from_attachments()
                if not new_embedding.count_tokens_a():
                    new_embedding.unlink()
                    raise UserError(_("Registro no creado debido a exceso de tokens."))
        return True
    

    