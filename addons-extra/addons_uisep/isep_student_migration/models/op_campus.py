# -*- coding: utf-8 -*-

from odoo import models, fields


class OpCampus(models.Model):
    _name = 'op.campus'
    _description = 'Campus'

    name = fields.Char(string='Nombre', size=128, required=True)
    code = fields.Char(string='Código', size=8, required=True)
    is_imported_record = fields.Boolean(default=False, string='¿Es registro importado de Odoo 12?')

    _sql_constraints = [('unique_campus_code', 'unique(code)', 'El código debe ser único por Sede !!!')]
