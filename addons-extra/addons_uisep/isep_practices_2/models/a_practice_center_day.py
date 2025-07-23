# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime



class PracticeCenterDay(models.Model):
    _name = 'practice.center.day'
    _description = 'Practice Center Day'

    day_of_week = fields.Selection(
        [('monday', 'Lunes'),
         ('tuesday', 'Martes'),
         ('wednesday', 'Miércoles'),
         ('thursday', 'Jueves'),
         ('friday', 'Viernes'),
         ('saturday', 'Sábado')],
        string="Días de la Semana",
        required=True,
        help="The day of the week when practices are available."
    )

    is_available = fields.Boolean(
        string="Available for Practice",
        default=True,
        help="Indicates whether practices can be done on this day."
    )

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = "%s" % (record.day_of_week)
    #         result.append((record.id, name))
    #     return result

    def name_get(self):
        result = []
        for record in self:
            day_dict = dict(self._fields['day_of_week'].selection)  # Obtiene el diccionario de selección
            name = day_dict.get(record.day_of_week, record.day_of_week)  # Traduce el valor técnico
            result.append((record.id, name))
        return result

