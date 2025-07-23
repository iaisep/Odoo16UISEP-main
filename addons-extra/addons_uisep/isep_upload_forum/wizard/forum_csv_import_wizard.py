# -*- coding: utf-8 -*-
import logging
import csv
import base64
from io import StringIO
from bs4 import BeautifulSoup

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ForumCsvImportWizard(models.TransientModel):
    _name = 'forum.csv.import.wizard'
    _description = _('ForumCsvImportWizard')

    forum_id = fields.Many2one('forum.forum')
    csv_file = fields.Binary('Archivo CSV', required=True)
    file_name = fields.Char('Nombre del archivo')


    def default_get(self, fields):
        c = super(ForumCsvImportWizard, self).default_get(fields)
        forum_id = self._context['get_forum_id']
        c['forum_id'] = forum_id
        return c

    def import_csv(self):
        if not self.csv_file:
            raise UserError("¡Por favor, suba un archivo CSV!")
        
        file_content = base64.b64decode(self.csv_file)
        file_content = file_content.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(file_content), delimiter=',')

        post_dict = {}

        for row in csv_reader:
            cleaned_message = BeautifulSoup(row['message'], "html.parser").get_text()

            message_with_user = f"<b>{row['userfullname']}</b> dice: {cleaned_message}"


            parent_post = None
            if row['subject'].startswith("Re: "):
                original_subject = row['subject'][4:].strip()
                parent_post = post_dict.get(original_subject)

            post = self.env['forum.post'].create({
                'name': row['subject'],
                'parent_id': parent_post.id if parent_post else False,
                'forum_id': self.forum_id.id,  # Utilizando la columna 'subject' como nombre
                'content': message_with_user,  # Utilizando la columna 'message' como descripción
                # Añadir más campos si es necesario
            })

            post_dict[row['subject']] = post

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
