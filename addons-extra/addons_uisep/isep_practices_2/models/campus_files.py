# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CampusFiles(models.Model):
    _name = 'campus.files'
    _description = 'CampusFiles'

    name = fields.Char(string="Nombre del archivo", compute='_compute_name', store=True)
    description = fields.Text(string="Descripción")
    file = fields.Binary(string="Archivo", required=True, attachment=True)
    file_name = fields.Char(string="Nombre del archivo")
    public = fields.Boolean(string='Publicar', default=False)


    @api.depends('file', 'file_name')
    def _compute_name(self):
        for record in self:
            if record.file_name:
                record.name = record.file_name
            else:
                record.name = "Archivo sin nombre"  #
