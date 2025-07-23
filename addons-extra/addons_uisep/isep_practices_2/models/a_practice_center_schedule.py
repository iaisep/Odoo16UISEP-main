# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class PracticeCenterSchedule(models.Model):
    _name = 'practice.center.schedule'
    _description = 'Practice Center Schedule'

    # Relación con el centro de práctica
    center_id = fields.Many2one(
        'practice.center',
        string="Practice Center",
        required=True,
        help="The practice center where the schedule is applied."
    )

    # Relación con los turnos disponibles
    shift_id = fields.Many2one(
        'practice.center.shift',
        string="Shift",
        required=True,
        help="The shift available for practice."
    )

    # Relación con los días disponibles para prácticas
    day_of_week_id = fields.Many2one(
        'practice.center.day',
        string="Day of the Week",
        required=True,
        help="The day of the week when practices are available."
    )

    # Hora de inicio de la práctica
    start_time = fields.Float(
        string="Start Time",
        required=True,
        help="The start time of the practice session in hours (e.g., 8.5 for 8:30 AM)."
    )

    # Hora de finalización de la práctica
    end_time = fields.Float(
        string="End Time",
        required=True,
        help="The end time of the practice session in hours (e.g., 12.5 for 12:30 PM)."
    )

    # Descripción opcional
    description = fields.Char(
        string="Description",
        help="A brief description of the practice schedule."
    )

