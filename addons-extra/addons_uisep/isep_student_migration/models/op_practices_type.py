# -*- coding: utf-8 -*-

from odoo import models, fields


class OpPracticesType(models.Model):
    _name = 'op.practices.type'
    _description = 'Tipo de prácticas'

    name = fields.Char(string='Nombre', size=128, required=True)
    is_imported_record = fields.Boolean(default=False, string='¿Es registro importado de Odoo 12?')
