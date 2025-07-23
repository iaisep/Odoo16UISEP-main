# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class PracticeCenterShift(models.Model):
    _name = 'practice.center.shift'
    _description = 'Practice Center Shift'

    name = fields.Selection(
        [('morning', 'Mañana'),
         ('afternoon', 'Tarde'),
         ('both', 'Ambos')],
        string="Turno",
        required=True,
        help="Defines the available shifts for the practice center."
    )

    description = fields.Char(
        string="Description",
        help="A brief description of the shift."
    )


    def name_get(self):
        result = []
        for record in self:
            day_dict = dict(self._fields['name'].selection)  # Obtiene el diccionario de selección
            name = day_dict.get(record.name, record.name)  # Traduce el valor técnico
            result.append((record.id, name))
        return result


