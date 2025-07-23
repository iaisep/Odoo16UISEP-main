from odoo import models, fields, api
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import io
import base64
import logging
_logger = logging.getLogger(__name__)

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    content_line_id = fields.Many2one('subject.content.line', string="Content line txt" )
    # content_line_ids = fields.Many2many('subject.content.line', string="Content Lines txt")    
    update_txt_slide = fields.Boolean('Txt requiere actualizar')

    
    def write(self, vals):
        for record in self:
            document_binary_content = vals.get('document_binary_content')
            html_content = vals.get('html_content')
            title_name = vals.get('name')
            slide_category = vals.get('slide_category', record.slide_category)
            if html_content or title_name and slide_category == 'article':
                vals['update_txt_slide'] = True
            elif document_binary_content or title_name and slide_category == 'document':
                vals['update_txt_slide'] = True
            
            if not document_binary_content and slide_category == 'document':
                vals['completion_time'] = 0.00
        return super(SlideSlide, self).write(vals) 
