# -*- coding: utf-8 -*-

from odoo import fields, models


class OpCourseType(models.Model):
    _name = 'op.course.type'

    name = fields.Char('Nombre', size=32, required=True)
    code = fields.Char('Código', size=12, required=True)
    is_imported_record = fields.Boolean(default=False, string='¿Es registro importado de Odoo 12?')

    _sql_constraints = [('unique_course_type_code', 'unique(code)', 'El código debe ser único por Tipo de curso !!!')]
