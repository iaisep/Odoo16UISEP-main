# -*- coding: utf-8 -*-

from odoo import api, fields, models


class OpBatch(models.Model):
    _inherit = 'op.batch'

    is_imported_record = fields.Boolean(default=False, string='¿Es registro importado de Odoo 12?')
    coordinator = fields.Many2one(comodel_name='res.partner', string='Coordinador')
    campus_id = fields.Many2one(comodel_name='op.campus', string='Sede')
    uvic_program = fields.Boolean(string='Programa UVIC', default=False)
    modality_id = fields.Many2one(comodel_name='op.modality', string='Modalidad')
    students_limit = fields.Integer(string='Límite matrículas')
    sepyc_program = fields.Boolean(string='Programa Sepyc / Sep', default=False)

    # INFORMACIÓN ACADÉMICA
    expiration_days = fields.Integer(string='Días de expiración', default=0)
    date_diplomas = fields.Datetime(string='Fecha de diplomas')
    academic_year = fields.Char(string='Año académico', size=16)
    generation = fields.Char(string='Generación', size=100)

    # SL
    hours = fields.Float(string='Horas')
    credits = fields.Float(string='Créditos')
    ects = fields.Float(string='ECTS', default=0)

    # RECONOCIMIENTOS
    acknowledgments = fields.Text(string='Reconocimientos', size=700)
    reconeixements = fields.Text(string='Reconoixements', size=700)

    # LATAM
    practical_hours_total = fields.Float(string='Total de horas prácticas')
    independent_hours_total = fields.Float(string='Total de horas independientes')
    theoretical_hours_total = fields.Float(string='Total de horas teóricas')
    hours_total = fields.Float(string='Total de horas')
    practical_hours_credits = fields.Float(string='Créditos horas prácticas')
    independent_hours_credits = fields.Float(string='Créditos horas independientes')
    theoretical_hours_credits = fields.Float(string='Créditos horas teóricas')
    credits_total = fields.Float(string='Total de créditos')

    # OTRA INFORMACIÓN
    days_week = fields.Char(string='Días de la semana', size=50)
    schedule = fields.Char(string='Horario', size=200)
    contact_class = fields.Char(string='Contacto', size=200)
    type_practices = fields.Many2one(comodel_name='op.practices.type', string='Tipo de prácticas')
