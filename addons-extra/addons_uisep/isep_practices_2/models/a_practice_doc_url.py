# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeDocUrl(models.Model):
    _name = 'practice.doc.url'
    _description = 'Practice Doc Url'

    name = fields.Char('Nombre')
    url_survey = fields.Char('Url Encuesta')
    practice_center_type_ids = fields.Many2many('practice.center.type', string="Tipos de Centro de Práctica")


