# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import fitz
from bs4 import BeautifulSoup
from docx import Document
from io import BytesIO
import os
from zipfile import ZipFile
import pandas as pd

class SurveySurvey(models.Model):
    _inherit= "survey.survey"

    active_ia=fields.Boolean("Activar IA")   
    
    general_instr = fields.Text(
        "Instrucción general", 
        default='Comparar dos textos, donde el Texto 1 es el contenido original (por ejemplo, una clase o lección) y el Texto 2 es un trabajo que hace referencia al Texto 1 (por ejemplo, una tarea o ensayo basado en la clase). La comparación debe considerar lo siguiente:\n\nRequisitos de presentación del ensayo:\n1. El ensayo deberá tener en la portada:\n   - Título del ensayo\n   - Nombre del alumno\n   - Nombre del módulo\n   - Nombre del profesor\n   - Fecha de entrega\n2. El ensayo deberá contar con:\n   - Introducción, desarrollo, conclusión y referencias en formato APA séptima edición. \n * Mostrar siempre los criterios que se tomaron para calificacion y comentario *'
    )

    criterio_califi = fields.Text(
        "Criterios de evaluación", 
        default="- Claridad y coherencia de ideas:\n  Nivel Excepcional (2.25 - 2.5 pts): Las ideas están expuestas de manera clara, lógica y coherente. La argumentación es sólida y bien estructurada.\n  Nivel Competente (2.0 - 2.24 pts): Las ideas son claras y coherentes en su mayoría. La argumentación es adecuada, con una estructura lógica.\n  Nivel Aceptable (1.75 - 1.99 pts): Las ideas son comprensibles, pero la coherencia es irregular. La argumentación tiene algunas debilidades.\n  Nivel Insuficiente (0 - 1.74 pts): Las ideas son confusas o inconsistentes. La argumentación es débil o carece de lógica.\n\n- Profundidad y rigor en el análisis:\n  Nivel Excepcional (2.25 - 2.5 pts): El análisis es profundo, crítico, y refleja un dominio claro de los temas seleccionados.\n  Nivel Competente (2.0 - 2.24 pts): El análisis es adecuado y refleja una buena comprensión de los temas seleccionados.\n  Nivel Aceptable (1.75 - 1.99 pts): El análisis es superficial o limitado, con algunas lagunas en la comprensión de los temas seleccionados.\n  Nivel Insuficiente (0 - 1.74 pts): El análisis es insuficiente, con poca o ninguna comprensión de los temas seleccionados.\n\n- Uso de fuentes académicas:\n  Nivel Excepcional (2.25 - 2.5 pts): Se utilizan más de tres fuentes académicas, correctamente citadas y relevantes, que enriquecen y respaldan la argumentación.\n  Nivel Competente (2.0 - 2.24 pts): Se utilizan al menos tres fuentes académicas relevantes, con una correcta citación, que respaldan la argumentación.\n  Nivel Aceptable (1.75 - 1.99 pts): Se utilizan menos de tres fuentes, o algunas fuentes no son académicas o no están bien citadas.\n  Nivel Insuficiente (0 - 1.74 pts): No se utilizan fuentes académicas o las citaciones son incorrectas.\n\n- Cumplimiento de Normas APA:\n  Nivel Excepcional (2.25 - 2.5 pts): El ensayo sigue rigurosamente las normas APA en todas las citas, referencias y formato general.\n  Nivel Competente (2.0 - 2.24 pts): El ensayo sigue mayormente las normas APA, con algunos errores menores en citaciones o formato.\n  Nivel Aceptable (1.75 - 1.99 pts): Hay varios errores en el uso de las normas APA, pero no comprometen gravemente la presentación.\n  Nivel Insuficiente (0 - 1.74 pts): El ensayo no sigue las normas APA o presenta múltiples errores que afectan la presentación.\n\n- Calidad y presentación del documento:\n  Nivel Excepcional (2.25 - 2.5 pts): El documento es de alta calidad, sin errores ortográficos o gramaticales, y bien presentado en formato Word.\n  Nivel Competente (2.0 - 2.24 pts): El documento es de buena calidad, con pocos errores ortográficos o gramaticales, y bien presentado.\n  Nivel Aceptable (1.75 - 1.99 pts): El documento tiene varios errores ortográficos o gramaticales, y la presentación es aceptable.\n  Nivel Insuficiente (0 - 1.74 pts): El documento tiene muchos errores ortográficos o gramaticales, o está mal presentado."
    )

    califi_final = fields.Text(
        "Calificación final", 
        default="Asigna una calificación unicamente al Texto 2 flotante del 1.0 al 10.0, donde 1.0 indica una referencia muy deficiente y 10.0 indica una referencia excelente. La calificación debe colocarse entre corchetes [ ].",
        help="Importante dejar que la IA deje la calificacion entre [] para que sea detectada por el sistema"
    )

    coment_final = fields.Text(
        "Comentario final", 
        default="Refierete al Texto 2 como 'Trabajo'. Proporciona un comentario objetivo y respetuoso sobre si el Trabajo ha sido correcto en su desarrollo, sin mencionar el texto 1 de referencia, enfocándote solo en los puntos de mejora, indicando fortalezas y áreas de mejora. El comentario debe colocarse entre llaves { }.",
        help="Importante dejar que la IA deje el comentario entre {} para que sea detectada por el sistema"
    )


    temp_califi=fields.Selection([('100','100% apegado al tema'),
                                  ('75', '75% apegado al tema'),
                                  ('50', '50% apegado al tema'),
                                  ('25', '25% apegado al tema'),
                                  ('1', '1% apegado al tema')], string="Rigides de calificacion", help='Indique que rigides calificara el adjunto')
    
    attachment_file = fields.Binary(string="Adjuntar Texto 1", help="Documentos compatibles, pdf, docx, doc, txt, pptx, ppt, xlsx")
    attachment_filename = fields.Char(string="Adjuntar Texto 1",help="Documentos compatibles, pdf, docx, doc, txt, pptx, ppt")

    attach_text_extract = fields.Text(string="Texto extraido")

    @api.onchange('attachment_file')
    def _extract_text_from_attachment(self):
        if self.attachment_file:
            file_content = base64.b64decode(self.attachment_file)
            file_extension = os.path.splitext(self.attachment_filename or '')[1].lower()

            if file_extension == '.pdf':
                self.attach_text_extract = self._extract_text_from_pdf(file_content)
            elif file_extension in ['.docx', '.doc']:
                self.attach_text_extract = self._extract_text_from_docx(file_content)
            elif file_extension == '.txt':
                self.attach_text_extract = self._extract_text_from_txt(file_content)
            elif file_extension in ['.pptx', '.ppt']:
                self.attach_text_extract = self._extract_text_from_pptx(file_content)
            elif file_extension in ['.xlsx', '.xls']:
                self.attach_text_extract = self._extract_text_from_excel(file_content, file_extension)
            else:
                self.attach_text_extract = 'Formato de archivo no soportado.'
        else:
            self.attach_text_extract = False

    def _extract_text_from_pdf(self, file_content):
        text = ""
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _extract_text_from_docx(self, file_content):
        text = ""
        with BytesIO(file_content) as f:
            doc = Document(f)
            for para in doc.paragraphs:
                text += para.text + "\n"
        return text

    def _extract_text_from_txt(self, file_content):
        return file_content.decode('utf-8')

    def _extract_text_from_pptx(self, file_content):
        text = ""
        with BytesIO(file_content) as f:
            with ZipFile(f) as pptx:
                for filename in pptx.namelist():
                    if filename.startswith("ppt/slides/slide"):
                        with pptx.open(filename) as slide:
                            soup = BeautifulSoup(slide.read(), "xml")
                            for elem in soup.find_all("a:t"):
                                text += elem.text + "\n"
        return text
    
    def _extract_text_from_excel(self, file_content, file_extension):
        text = ""
        with BytesIO(file_content) as f:
            if file_extension == '.xls':
                excel_data = pd.ExcelFile(f, engine='xlrd')
            else:
                excel_data = pd.ExcelFile(f)  # .xlsx usa openpyxl por defecto
            for sheet_name in excel_data.sheet_names:
                text += f"--- Hoja: {sheet_name} ---\n"
                df = pd.read_excel(f, sheet_name=sheet_name, engine='xlrd' if file_extension == '.xls' else None)
                text += df.to_csv(index=False)  # Convertimos DataFrame a texto delimitado por comas
                text += "\n\n"
        return text