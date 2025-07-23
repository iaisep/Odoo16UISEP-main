# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpCourse(models.Model):
    _inherit = "op.course"

    education_level = fields.Selection([('profesional','Profesional Asociado'),('tecnico','Técnico Superior Universitario'),('licenciatura','Licenciatura'),('especialidad','Especialidad'),('maestria','Maestria'),('doctorado','Doctorado')], string="Nivel Educativo")
    career_key = fields.Char(string="Clave de Carrera")
    institute_key = fields.Char(string="Clave de Institución")
    rvoe_number = fields.Char(string="Número de RVOE")
    rvoe_date = fields.Date(string="Fecha de RVOE")
    
