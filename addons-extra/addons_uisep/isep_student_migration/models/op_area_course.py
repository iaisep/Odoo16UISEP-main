# -*- coding: utf-8 -*-

from odoo import fields, models


class OpAreaCourse(models.Model):
    _name = 'op.area.course'

    name = fields.Char(string="Nombre de Área")
    code = fields.Char(string="Código de Área")
    is_imported_record = fields.Boolean(default=False, string='¿Es registro importado de Odoo 12?')

    _sql_constraints = [('unique_area_code', 'unique(code)', 'El código debe ser único por Área de curso !!!')]
