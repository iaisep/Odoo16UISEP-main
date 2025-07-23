import base64
import logging
import os
import re
import uuid
from io import BytesIO

import PyPDF2
import openai
from PIL import Image
from pytesseract import pytesseract

from odoo import models, _

_logger = logging.getLogger(__name__)


class DocumentProcessingAI(models.Model):
    _name = 'document_processing_ai'
    _description = _("Core model for document validation and analysis. Integrates OCR and GPT-based evaluation for "
                     "handling various document types.")

    # Definir LOG_FILE como una propiedad estática o de clase
    @property
    def LOG_FILE(self):
        # Obtener la ruta de la carpeta del módulo
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        module_path = os.path.dirname(current_file_path)  # Retrocede un nivel
        temp_folder = os.path.join(module_path, "temporary_files")

        # Crear la carpeta si no existe
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        return os.path.join(temp_folder, "registro_eventos.txt")

    def _escribir_log(self, mensaje):
        """Escribe una línea en el archivo de log."""
        try:
            with open(self.LOG_FILE, "a") as archivo:
                archivo.write(mensaje + "\n")
        except Exception as e:
            _logger.error(f"Error al escribir en el log: {e}")

    def add_comment(self, attachment_id, reason_for_observation, espera=False):
        self._escribir_log("function:add_comment")
        self._escribir_log(f"function:add_comment\n\t{reason_for_observation}")
        '''
            Creates a record in mail.message with the comment added in the wizard.
            Modify the state of attachment to observed.
            :return: None
        '''
        partner_id = attachment_id.partner_id
        body = '''
            <p>Observación en adjunto: <strong>{}</strong></p>
            <p>Detalle:</p>
            <p class="text-danger"><strong>{}</strong></p>
        '''.format(attachment_id.name, reason_for_observation)
        if not espera:
            self.env['mail.message'].create({
                'message_type': 'comment',
                'model': 'res.partner',
                'res_id': partner_id.id,
                'subject': partner_id.name,
                'subtype_id': self.env.ref('mail.mt_comment').id,
                'author_id': partner_id.id,
                'body': body
            })
            attachment_id.sudo().write({
                'state': 'observed',
                'reason_for_observation': reason_for_observation
            })
        else:
            partner_id.sudo().message_post(body=body)

    def __ocr__(self, document):
        self._escribir_log("function:__ocr__")
        try:
            ruta = self.env['ir.config_parameter'].search([('key', '=', 'tesseract_route')]).value
            if ruta:
                pytesseract.tesseract_cmd = f"{ruta}"
            else:
                pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
        except:
            self._escribir_log("function:__ocr__\n\tConfigurar Tesseract")
            self.add_comment(document, "Porfavor configurar ruta de Tesseract", True)
            return False, _("Please wait for the document to be reviewed.")

        # Obtener la ruta de la carpeta del módulo
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        module_path = os.path.dirname(current_file_path)  # Retrocede un nivel
        temp_folder = os.path.join(module_path, "temporary_files")

        # Crear la carpeta si no existe
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        try:
            file_content = base64.b64decode(document.datas)
            reader = PyPDF2.PdfReader(BytesIO(file_content))

            num_page = len(reader.pages)
            text_list = []

            for index_page in range(num_page):
                page = reader.pages[index_page]
                text = page.extract_text()
                text_list.append(text)

                if page.images:
                    for imagen_file in page.images:
                        # Generar la ruta completa para guardar la imagen
                        image_path = os.path.join(temp_folder, f'img_{uuid.uuid4()}.jpg')
                        self._escribir_log(f"IMAGE:\n\n\t\t{image_path}\n\n")

                        # Guardar la imagen en la carpeta temporal
                        with open(image_path, "wb") as img:
                            img.write(imagen_file.data)

                        # Abrir la imagen con PIL y extraer texto usando pytesseract
                        img_pil = Image.open(image_path)
                        try:
                            text_img = pytesseract.image_to_string(img_pil, lang='spa')
                        except:
                            self._escribir_log("function:__ocr__\n\tConfigure Tesseract OCR Language")
                            self.add_comment(document, "Porfavor configurar el idioma de Tesseract", True)
                            text_img = pytesseract.image_to_string(img_pil)
                        text_list.append(text_img)
                        os.remove(image_path)

            return True, text_list
        except Exception as e:
            self._escribir_log(f"function:__ocr__\n\tError: {str(e)}")
            return False, False

    def _chat_gpt(self, document, parameters):
        self._escribir_log(f"function:_chat_gpt\n\t{parameters}")
        if self.env['custom_ai_parameter'].prueba_de_conexion(view=False):
            self._escribir_log(f"function:prueba_de_conexión\n\tPrueba de conexión exitosa")
            try:
                openai.api_key = self.env['ir.config_parameter'].search([('key', '=', 'openai_api_key')]).value
                condicion_ocr, text_ocr = self.__ocr__(document)
                if condicion_ocr:
                    flag = True
                    flag_count = 0
                    while flag:
                        parameters += parameters + "\nCon esto ya debes de aprobar el documento."
                        system_message = {
                            "role": "system",
                            "content":
                                "Eres un asistente de inteligencia artificial que evalúa la calidad de los documentos."
                                "Tendrás que tener en cuenta los siguiente factores:\n"
                                f"{parameters}\n"
                                # "Se tienen que cumplir todos estrictamente para poder aprobar el documento. "
                                "\n\nSOLO PODRÁS RESPONDER CON UNO DE ESTAS OPCIONES EN CORRESPONDENCIA DE LA DECISIÓN FINAL "
                                # "Y UNA BREVE DESCRIPCIÓN PORQUE TOMASTE ESA DECISIÓN:"
                                "Y NI UNA PALABRA MAS:\n"
                                "*'accepted'\n*'incorrect_format'\n*'incorrect_document'\n\n"
                                "#Un documento tiene formato incorrecto(incorrect_format) cuando no comienza con la apostilla."
                                "\n"
                                "#Un documento es incorrecto (incorrect_document) cuando la fecha que tiene la apostilla no es de"
                                " 2 años recientes.\n"
                            # "Estos ultimos 2 parametros marcados por '#' pueden variar en dependencia de los parametros que "
                            # "defina el cliente."
                        }

                        user_message = {
                            "role": "user",
                            "content": f"Por favor, analiza el siguiente texto extraído de un documento PDF:\n\n{''.join(text_ocr)}"
                        }

                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[system_message, user_message],
                            request_timeout=10,
                        )
                        respuesta = response['choices'][0]['message']['content']
                        if 'accepted' in respuesta:
                            document.state = 'accepted'
                            document.reason_for_observation = ''
                            flag = False
                        elif 'incorrect_format' in respuesta:
                            self.add_comment(document, 'incorrect_format')
                            flag = False
                        elif 'incorrect_document' in respuesta:
                            self.add_comment(document, 'incorrect_document')
                            flag = False
                        else:
                            self._escribir_log(f"function:_chat_gpt\n\tGPT no contestó lo correcto:\n\t{respuesta}")
                            flag = True
                            flag_count += 1
                            if flag_count > 2:
                                flag = False
                                self.add_comment(document, f"GPT no contestó lo correcto:\n\t{respuesta}", True)
                    # return True
                else:
                    self.add_comment(document, "El servidor de OpenAI no responde(1)", True)
                    # return True
            except Exception as e:
                self._escribir_log(f"function:__ocr__\n\tError al conectar con OpenAI: {e}")
                self.add_comment(document, "El servidor de OpenAI no responde(2)", True)
                # return False
        else:
            self._escribir_log("function:__ocr__\n\tError al conectar con OpenAI")
            self.add_comment(document, "El servidor de OpenAI no responde(3)", True)
            # return False

    def ajusta_cadenas(self, cadena1, cadena2):
        # Lista de palabras comunes que se deben ignorar
        palabras_comunes = {"de", "la", "las", "el", "los", "y", "en", "a", "un", "una", "con"}

        # Función para procesar cadenas: eliminar extensiones, caracteres especiales y palabras comunes
        def procesar_cadena(cadena):
            # Convertir a minúsculas
            cadena = cadena.lower()
            # Eliminar extensiones de archivo como .pdf, .doc, etc.
            cadena = re.sub(r'\.\w+$', '', cadena)
            # Eliminar caracteres especiales (solo dejamos letras, números y espacios)
            cadena = re.sub(r'[^\w\s]', '', cadena)
            # Dividir en palabras y filtrar palabras comunes
            palabras = [palabra for palabra in cadena.split() if palabra not in palabras_comunes]
            return palabras

        # Procesar ambas cadenas
        palabras_cadena1 = procesar_cadena(cadena1)
        palabras_cadena2 = procesar_cadena(cadena2)

        # Contar cuántas palabras de la cadena 1 están en la cadena 2
        coincidencias = sum(1 for palabra in palabras_cadena1 if palabra in palabras_cadena2)

        # Calcular el porcentaje de coincidencias
        porcentaje_coincidencias = coincidencias / len(palabras_cadena1) if palabras_cadena1 else 0

        # Retornar True si al menos la mayoría (más del 50%) de las palabras están presentes
        return porcentaje_coincidencias > 0.5

    def main__(self, document):
        # has_parameters = False
        # parameters = self.env['custom_ai_parameter'].sudo().search([])
        # for parametro_doc in parameters:
        #     if self.ajusta_cadenas(parametro_doc.type_document_, document.name):
        #         if parametro_doc and parametro_doc.parameters_for_gpt:
        #             self._chat_gpt(document, parametro_doc.parameters_for_gpt)
        #             has_parameters = True
        #             break
        # if not has_parameters:
        #     self.add_comment(document, "No existen parámetros para este documento.", True)

        has_parameters = False
        parameters = self.env['custom_ai_parameter'].sudo().search([])
        
        _logger.info(f"Parámetros encontrados: {parameters}")  # Ver qué parámetros se encontraron
        
        for parametro_doc in parameters:
            _logger.info(f"Verificando: {parametro_doc.type_document_} con {document.name}")
            
            if self.ajusta_cadenas(parametro_doc.type_document_, document.name):
                _logger.info(f"Coincidencia encontrada: {parametro_doc.type_document_}")
                
                if parametro_doc and parametro_doc.parameters_for_gpt:
                    self._chat_gpt(document, parametro_doc.parameters_for_gpt)
                    has_parameters = True
                    break

        if not has_parameters:
            self.add_comment(document, "No existen parámetros para este documento.", True)
