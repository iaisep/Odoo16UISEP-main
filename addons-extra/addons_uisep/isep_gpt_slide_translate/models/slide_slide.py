
# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError
from bs4 import BeautifulSoup

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    translate_with_gpt = fields.Boolean(string="Traducido con GPT")

    # aqui si usamos BeautifulSoup es mas efiente
    def _html_content_treatment(self, html_content):
        if not html_content:
            raise UserError("Html_content invalido.")
        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup.find_all(class_='o_conditional_hidden'):
            if 'o_conditional_hidden' in element['class']:
                element['class'].remove('o_conditional_hidden')
                if not element['class']:
                    del element['class']
        return str(soup)

    """def _html_content_treatment(self, html_content):
        if not html_content:
            raise UserError("Html_content inválido.")

        # Analizar el HTML con lxml
        parser = HTMLParser(encoding="utf-8")
        root = html.fromstring(html_content, parser=parser)

        # Buscar todos los elementos con la clase 'o_conditional_hidden'
        for element in root.xpath('//*[@class]'):
            classes = element.attrib.get('class', '').split()
            if 'o_conditional_hidden' in classes:
                # Eliminar la clase 'o_conditional_hidden'
                classes.remove('o_conditional_hidden')
                if classes:
                    # Si quedan otras clases, actualizamos el atributo
                    element.attrib['class'] = ' '.join(classes)
                else:
                    # Si no quedan clases, eliminamos el atributo 'class'
                    del element.attrib['class']

        # Convertir de nuevo a cadena HTML
        return html.tostring(root, pretty_print=False, encoding="unicode")"""

    def action_open_translation_wizard(self):     
        self.ensure_one()
        html_content = self._html_content_treatment(self.with_context(lang='es_MX').html_content)
        es_mx = self.env.ref('base.lang_pt_BR').id
        translate_id = self.env['wizard.slide.translate'].create({
            'slide_id': self.id,
            'name': self.with_context(lang='es_MX').name,
            'html_es_mx': html_content,
            'langs_id': (4, es_mx)
            
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Asistente para Traducción',
            'res_model': 'wizard.slide.translate',
            'view_mode': 'form',
            'res_id': translate_id.id,
            'target': 'current',
        }

    