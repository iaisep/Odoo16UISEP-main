from odoo import models, api
# import PyPDF2
from PyPDF2 import PdfFileReader
# import re
# import base64
import io


class SignTemplate(models.Model):
    _inherit = "sign.template"

    @api.model
    def _get_pdf_number_of_pages(self, pdf_data):
        file_pdf = PdfFileReader(io.BytesIO(pdf_data), strict=False, overwriteWarnings=False)
        return len(file_pdf.pages)  # file_pdf.getNumPages()