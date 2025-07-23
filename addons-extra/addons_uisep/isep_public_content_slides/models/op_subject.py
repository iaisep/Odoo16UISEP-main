# knowledge_content.py
from odoo import models, fields, api
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import io
import base64
import logging
_logger = logging.getLogger(__name__)


class OpSubject(models.Model):
    _inherit = 'op.subject'

    