# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpAdmission(models.Model):
    _inherit = "op.admission"

    admission_status = fields.Selection([('ins','Inscripción'),('reins','Reinscripción')], string="Estatus")
    special_needs = fields.Selection([('na','No Aplica'),('disabled','Con discapacidad'),('outstanding','Con aptitudes sobresalientes')],string="Necesidades Educativas Especiales")
    academic_background = fields.Selection([('si','Si'),('no','No'),('no_aplica','No Aplica')], string="Presenta Antecedentes Académicos")
    generation = fields.Selection([
        ('1','2021'),
        ('2','2022'),
        ('3','2023'),
        ('4','2024'),
        ('5','2025'),
        ('6','2026'),
        ('7','2027')], string="Generación")
        
    period_4month = fields.Selection([
        ('1','Primero'),
        ('2','Segundo'),
        ('3','Tercer')], string="Cuatrimestre")
    
