# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DataMasterCall(models.Model):
    _name = 'data.master.call'
    _description = 'DataMasterCall'

    name_team = fields.Char('Nombre de equipo')
    modules_consult = fields.Text('Módulos a consultar')
    articles_ai = fields.Text('Artículos de la IA')



    def action_send_data_call(self):
        
        data = self.env['data.master.call']
        teams = self.env['helpdesk.team'].search([('activate_gpt', '=', True)])
        for team in teams:
            consult_blocks = [f"[Módulo: {consult.name}]" for consult in team.config_consult_ids]
            consult_names = ', '.join(consult_blocks)

            article_blocks = [f"[Título: {article.name}, Texto extraido: {article.convert}]" for article in team.article_embeding_ids]
            article_names = ', '.join(article_blocks)

            existing_record = data.search([
                    ('name_team', '=', team.name),
                ])

            values = {
                'name_team': team.name,
                'modules_consult':consult_names,
                'articles_ai':article_names,
            }

            if existing_record:
                existing_record.write(values)
            else:
                data.create(values)


