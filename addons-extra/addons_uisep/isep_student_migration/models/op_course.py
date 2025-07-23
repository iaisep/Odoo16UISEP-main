# -*- coding: utf-8 -*-

from odoo import fields, models


class OpCourse(models.Model):
    _inherit = 'op.course'

    sepyc_program = fields.Boolean(string='Programa oficial', default=False)
    course_type_id = fields.Many2one(comodel_name='op.course.type', string='Tipo de curso')
    area_id = fields.Many2one(comodel_name='op.area.course', string='Área de curso')
    is_imported_record = fields.Boolean(default=False, string='¿Es registro importado de Odoo 12?')
