# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpBatch(models.Model):
    _inherit = "op.batch"

    company_type = fields.Selection([('fuisep','FUISEP'),('uisep','UISEP')], string="Tipo de Empresa")
    scholar_year = fields.Char(string="Año Escolar")
    cct = fields.Selection([('si','Si'),('no','No'),('no_aplica','No Aplica')], string="CCT")
    educational_mod = fields.Selection([('escolar','Escolar'),('no_escolar','No Escolarizada'),('mixta','Mixta')], string="Modalidad Educativa")
    shift_type = fields.Selection([('matutino','Matutino'),('vespertino','Vespertino'),('mixto','Mixto')], string="Turno")
    
