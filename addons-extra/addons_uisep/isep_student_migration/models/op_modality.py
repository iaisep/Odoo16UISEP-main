# -*- coding: utf-8 -*-

from odoo import models, fields


class OpModality(models.Model):
    _name = 'op.modality'
    _description = 'Modalidad'

    name = fields.Char(string='Nombre', size=128, required=True)
    code = fields.Char(string='Código', size=8, required=True)
    new_code = fields.Char(string='Nuevo código', size=8, required=True)
    analytic_code = fields.Char(string='Código analítico', size=8, required=True)
    is_imported_record = fields.Boolean(default=False, string='¿Es registro importado de Odoo 12?')

    _sql_constraints = [('unique_modality_code', 'unique(code)', 'El código debe ser único por Modalidad !!!')]
