# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class PracticeCenterTypes(models.Model):
    _name = 'practice.center.type'
    _description = 'Practice Center Type'

    type_of_practice = fields.Selection([
        ('on_site', 'Presencial'),
        ('distance', 'Distancia'),
        ('validation', 'Convalidación'),
        # ('on_site_spain', 'Presencial España')
    ], default='on_site')

    is_available = fields.Boolean(
        string="Available for Practice",
        default=True,

    )
    center_id = fields.Many2one(
        'practice.center',
        string="Practice Center",
        help="The practice center where the type is applied."
    )

    expected_ids = fields.One2many(
        comodel_name="practice.center.expected",
        inverse_name="practice_center_type_id",
        string="Expected Activities or Documents",
        help="Expected Activities or Documents por Type of practices"
    )

    description = fields.Text(
        string="Requisites",
        help="A brief of Requisites."
    )

    total_hours = fields.Float(
        string="Total hours for Practice ",
        help="Total hours of practices",

    )

    op_course_ids = fields.Many2many(
        comodel_name="op.course",
        string="Courses",
        help="Course related to this Modality."
    )

    enabled_center_ids = fields.Many2many(
        'practice.center',
        string="Enabled Practice Centers",
        compute="_compute_enabled_center_ids",
        help="The practice centers where the type is applied."
    )

    @api.depends('center_id', 'op_course_ids')
    def _compute_enabled_center_ids(self):
        for record in self:
            # Buscar los registros en 'practice.center.type'
            matching_types = self.env['practice.center'].search([('type_ids','in',record.id),
                                                                 ('op_course_ids','in',record.op_course_ids.ids)])
            print(matching_types.op_course_ids)
            print(record.op_course_ids)

            # Asignar los centros encontrados al campo Many2many
            record.enabled_center_ids = [(6, 0, matching_types.ids)]  # Formato Many2many para asignar varios registros
            print(record.enabled_center_ids)


    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = "%s" % (record.type_of_practice)
    #         result.append((record.id, name))
    #     return result

    def name_get(self):
        result = []
        for record in self:
            day_dict = dict(self._fields['type_of_practice'].selection)  # Obtiene el diccionario de selección
            name = day_dict.get(record.type_of_practice, record.type_of_practice)  # Traduce el valor técnico
            result.append((record.id, name))
        return result
