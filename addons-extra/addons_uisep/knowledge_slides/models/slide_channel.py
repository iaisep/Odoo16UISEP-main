from odoo import models, fields, api
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import io
import base64
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    required_update_article = fields.Boolean(string="Required update ")
    
    def write(self, vals):
        for record in self:
            document_binary_content = vals.get('document_binary_content')
            html_content = vals.get('html_content')
            slide_category = vals.get('slide_category', record.slide_category)
            if html_content and slide_category == 'article':
                vals['required_update_article'] = True
            elif document_binary_content and slide_category == 'document':
                vals['required_update_article'] = True

            
            if not document_binary_content and slide_category == 'document':
                vals['completion_time'] = 0.00
        return super(SlideSlide, self).write(vals) 

    @api.model
    def create(self, vals):
        document_binary_content = vals.get('document_binary_content')
        html_content = vals.get('html_content')
        slide_category = vals.get('slide_category')
        if html_content and slide_category == 'article':
            vals['required_update_article'] = True
        elif document_binary_content and slide_category == 'document':
            vals['required_update_article'] = True
        return super(SlideSlide, self).create(vals)
    

    def sync_slide_to_knowledge_v2(self,limit):
        root = self.env['knowledge.article'].search([('generated_from_content_root','=',True)], limit=1)
        if not root:
            root = self.env['knowledge.article'].create({
                'name': 'CONTENIDO ELEARNING',
                'is_published': True,
                'category': 'private',
                'generated_from_content_root':True
            })
        slides = self.search([('required_update_article', '=', True)], limit=limit)
        channels = slides.mapped('course_id').filtered(lambda x: x.exclude_from_articles != False)
        for channel in channels:
            if channel.slide_ids:                
                if not channel.article_id:
                    channel.article_id = self.env['knowledge.article'].create({
                        'name': channel.name,
                        'is_published': True,
                        'parent_id': root.id,
                        'category': 'private',
                        'generated_from_content': True,
                        'body': channel.processing_content(channel.slide_ids),
                    })                
                else:                    
                    channel.article_id.write({
                            'name': channel.name,
                            'body': channel.processing_content(channel.slide_ids),
                        })
            channel.slide_ids.required_update_article = False
            channel.required_update_article = False
        


        
            
class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    article_id = fields.Many2one('knowledge.article', string="Articulo" )
    exclude_from_articles = fields.Boolean(string="Excluir del modulo de conocimiento", store=True, index=True)
    required_update_article = fields.Boolean(string="Required update ", compute="compute_required_update_article", default=True, store=True , index=True)

    @api.depends('slide_ids.required_update_article')
    def compute_required_update_article(self):        
        for record in self:
            if record.required_update_article == False:
                record.required_update_article = any(slide.required_update_article for slide in record.slide_ids)                
        

    def extract_text_from_pdf(self, document_binary_content):
        if not document_binary_content:
            return "_pdf_"
        pdf_content = io.BytesIO(base64.b64decode(document_binary_content))
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        except Exception as e:
            return "_pdf_"
        extracted_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            extracted_text += page.get_text() + "\n"
        pdf_document.close()
        return extracted_text
    
    def processing_content(self, slide_ids):
        body = []
        for ss in slide_ids:
            if ss.slide_category == 'article':
                if ss.html_content:
                    body.append(str(BeautifulSoup(ss.html_content, "html.parser").get_text(separator=" ")))
                else:
                    body.append('')
            elif ss.slide_category == 'document':
                try:
                    body.append(self.extract_text_from_pdf(ss.document_binary_content))
                except Exception as e:
                    _logger.error(f"Error extracting text from PDF: {e}")
                    body.append('')
            #ss.required_update_article = False
        return '\n'.join(body)


    
    def sync_slide_to_knowledge(self, limit):
        root = self.env['knowledge.article'].search([('generated_from_content_root','=',True)], limit=1)
        if not root:
            root = self.env['knowledge.article'].create({
                'name': 'CONTENIDO ELEARNING',
                'is_published': True,
                'category': 'private',
                'generated_from_content_root':True
            })

        exclude = self.search([('exclude_from_articles', '=', True)])
        unique_article_ids = exclude.mapped('article_id').filtered(lambda article: article)
        unique_article_ids.unlink()

        channels = self.search([ ('exclude_from_articles', '=', False),('required_update_article', '=', True)], limit=limit)     
        for channel in channels:
            if channel.slide_ids:                
                if not channel.article_id:
                    channel.article_id = self.env['knowledge.article'].create({
                        'name': channel.name,
                        'is_published': True,
                        'parent_id': root.id,
                        'category': 'private',
                        'generated_from_content': True,
                        'body': self.processing_content(channel.slide_ids),
                    })                
                else:                    
                    channel.article_id.write({
                            'name': channel.name,
                            'body': self.processing_content(channel.slide_ids),
                        })
            channel.slide_ids.required_update_article = False
            channel.required_update_article = False
                
            

