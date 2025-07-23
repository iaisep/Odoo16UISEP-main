# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpStudent(models.Model):
    _inherit = "op.student"

    annex_9 = fields.Boolean(string="En anexo 9")
    certificate_type = fields.Selection([('ct','Certificado Total'),('cp','Certificado Parcial'),('tp','Título Profesional'),('dp','Diploma'),('gr','Grado')], string="Tipo de Certficado")
    
