# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpCourse(models.Model):
    _inherit = "op.course"

    #code_moodle=fields.Char(string="Codigo")
    #category_moodle_number=fields.Char(string='URL Categoria Moodle')
    #category_moodle=fields.Char(string='URL Categoria Moodle')
    op_category_id=fields.Many2one("op.category",string="Area del curso")
    moodle_category_ids=fields.One2many("op.moodle.category","course_id",string="Moodle Categorias")
    batch_ids=fields.One2many("op.batch","course_id",string="Grupos")

class OpMoodleCategory(models.Model):
    _name = "op.moodle.category"

    course_id=fields.Many2one("op.course",string="Curso")
    op_category_id=fields.Many2one("op.category",string="Area")
    code_moodle=fields.Char(string="Codigo")
    category_moodle_number=fields.Char(string='Categoria Moodle ID')
    option=fields.Selection([('all','Todos los modulos'),('custom','Personalizado')],string="Opcion",required=True)
    modules_ids=fields.Char(string="Modulos IDS")
    category_moodle=fields.Char(string='URL Categoria Moodle')
    company_ids=fields.Many2many("res.company",string="Compañia")
    