# knowledge_content.py
from odoo import models, fields, api
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import io
import base64
import logging
import re
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)



class SubjectContentLine(models.Model):
    _name = 'subject.content.line'
    _description = 'Content txt of Slide.Slide'

    name = fields.Char(string="Nombre", required=True)
    slide_id = fields.Many2one('slide.slide', string="Contenido Elearning", required=True, ondelete="cascade")
    is_document = fields.Boolean(string="Es PDF")
    html_content = fields.Text('Texto')

    def convert_slide_to_txt(self, limit):
        slides = self.env['slide.slide'].search([
                    '|',
                    ('update_txt_slide', '=', True),
                    ('content_line_id', '=', False),
                    ('channel_id.op_subject_ids', '!=', False),
                    ('is_published', '=', True),
                    ('is_category', '=', False),
                    ('slide_category', 'in', ['article', 'document']),
                ], limit=limit)

        if not slides:
            raise UserError("No hay contenido pendiente por convertir a txt.")

        for slide in slides:
            if slide.content_line_id:            
                slide.content_line_id.name = slide.with_context(lang='es_MX').name.replace('\x00', '') or slide.name.replace('\x00', '')
                slide.content_line_id.html_content = self.processing_content(slide).replace('\x00', '')
                slide.update_txt_slide = False
                #slide.env.cr.commit()
                
            else:
                content_line_id = self.env['subject.content.line'].create({
                        'name': slide.with_context(lang='es_MX').name.replace('\x00', '') or slide.name.replace('\x00', ''),
                        'slide_id': slide.id,
                        'html_content': self.processing_content(slide).replace('\x00', '')

                    })
                slide.content_line_id = content_line_id.id
                slide.update_txt_slide = False
                #slide.env.cr.commit()

            

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
    
    def processing_content(self, slide):
        body = ""
        if slide.slide_category == 'article':
            if slide.html_content:
                body = str(BeautifulSoup(slide.with_context(lang='es_MX').html_content or slide.html_content, "html.parser").get_text(separator=" "))
            else:
                body = ""
        elif slide.slide_category == 'document':
            self.is_document = True
            try:
                body = self.extract_text_from_pdf(slide.document_binary_content)
            except Exception as e:
                _logger.error(f"Error extracting text from PDF: {e}")
                body = ""
        try:
            body = body.replace('\n', '').strip()
            body = re.sub(r'\s+', ' ', body)
        except Exception as e:
            _logger.error(f"Error extracting text from PDF: {e}")

        return body
