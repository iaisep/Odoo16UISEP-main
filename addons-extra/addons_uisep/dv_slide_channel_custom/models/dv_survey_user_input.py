# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64
import fitz
from bs4 import BeautifulSoup
from docx import Document
from io import BytesIO
import os
from zipfile import ZipFile
import pandas as pd
from odoo.tools import html2plaintext
import json
import requests
import logging
import re
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class SurveyUserInput(models.Model):
    _inherit= "survey.user_input"

    active_ia=fields.Boolean("Activada IA", related='survey_id.active_ia') 
    score_ia=fields.Float("Nota sugerida IA")
    extrae_alum=fields.Text("Texto 2")
    error_ai=fields.Text("Error en procesar con IA")    
    resumen_ia=fields.Text("Resumen IA",help="Puede modificar el resultado de la IA pero mantenga la estrutura Calificacion entre '[]' y Comentario dentro de '{}'")


    def _clean_null_chars(self, text):
        """Limpia caracteres NULL (\x00) de un texto."""
        return text.replace('\x00', '') if text else ''

    def analyze_score_test(self):        
        config = self.env['dv.config.ia'].search([], limit=1)
        if not config or not config.token_id:
            raise UserError(_('Por favor, configure el token de la API de OpenAI en la configuración de Configuration GPT.'))
        
        prompt = "{} {} {} {}".format(
            self.survey_id.general_instr,
            self.survey_id.criterio_califi,
            self.survey_id.califi_final,
            self.survey_id.coment_final
        )

        text1= self.survey_id.attach_text_extract if self.survey_id.attach_text_extract else html2plaintext(self.survey_id.description or '')
        print("////////////////////////////////////",text1)
        text_analize = "Texto 1 = {} Texto 2 = {}".format(
            self._clean_null_chars(text1), 
            self._clean_null_chars(self.extrae_alum)
        )
           
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config.token_id}'
        }
        
        data = {
            "model": config.model_ia,
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": text_analize}],
            "temperature": config.temp_chat
        }

        try:            
            response = requests.post(config.url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            response_data = response.json()

            ai_response_content = self._clean_null_chars(response_data['choices'][0]['message']['content'])
            self.resumen_ia = ai_response_content

        except requests.exceptions.RequestException as e:
            raise UserError(_('Error al conectar con la API de OpenAI: %s') % e)



    def extract_text_from_attachment(self):
        if self.user_input_line_ids:
            for line in self.user_input_line_ids:
                if line.value_file_ids:
                    for archivo in line.value_file_ids:
                        file_content = base64.b64decode(archivo.datas)
                        file_extension = os.path.splitext(line.filename or '')[1].lower()
                        if file_extension == '.pdf':
                            self.extrae_alum = self._clean_null_chars(self._extract_text_from_pdf(file_content))
                        elif file_extension in ['.docx', '.doc']:
                            self.extrae_alum = self._clean_null_chars(self._extract_text_from_docx(file_content))
                        elif file_extension == '.txt':
                            self.extrae_alum = self._clean_null_chars(self._extract_text_from_txt(file_content))
                        elif file_extension in ['.pptx', '.ppt']:
                            self.extrae_alum = self._clean_null_chars(self._extract_text_from_pptx(file_content))
                        elif file_extension in ['.xlsx', '.xls']:
                            self.extrae_alum = self._clean_null_chars(self._extract_text_from_excel(file_content, file_extension))
                        else:
                            self.extrae_alum = 'Formato de archivo no soportado.'
                        break
                else:
                    self.extrae_alum = 'No hay archivos adjuntos en esta línea de entrada.'

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
                text += df.to_csv(index=False)  # Convertir DataFrame a texto delimitado por comas
                text += "\n\n"
        return text
    
    
    def use_extract_score_and_comment(self):
        for record in self:
            if record.resumen_ia:
                # Buscar la calificación en corchetes [7.5]
                score_match = re.search(r'\[([\d.]+)\]', record.resumen_ia)               
                if score_match:
                    record.score_ia = float(score_match.group(1))  
    
    def use_extract_comment(self):
        for record in self:
            if record.resumen_ia:
                # Buscar el comentario dentro de las llaves { }
                comment_match = re.search(r'\{(.+?)\}', record.resumen_ia)
                if comment_match:
                    record.comment = comment_match.group(1).strip()                


    def update_answer_scores(self):
        self.use_extract_comment()
        for record in self:            
            if record.user_input_line_ids:
                for line in record.user_input_line_ids:
                    line.answer_score = record.score_ia  


    def cron_ia_score_survey(self,limit):
        surveys = self.search([('active_ia', '=', True), ('resumen_ia', '=', False), ('error_ai', '=', False)], limit=limit )
        config = self.env['dv.config.ia'].search([], limit=1)
        for survey in surveys:
            try:
                survey.extract_text_from_attachment()
                survey.analyze_score_test()
                survey.use_extract_score_and_comment()
                if config and config.auto_score:
                    survey.update_answer_scores()                    
            except Exception as e:
                _logger.error(f"Error procesando la encuesta {survey.id}: {e}")
                survey.error_ai = self._clean_null_chars(str(e))


    def analiza_a_mano_survey(self):
        if self.active_ia == True:
            self.extract_text_from_attachment()
            self.analyze_score_test()
            self.use_extract_score_and_comment()            
