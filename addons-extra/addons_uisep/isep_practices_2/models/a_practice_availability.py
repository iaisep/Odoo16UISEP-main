# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime




class PracticeAvailability(models.Model):
    _name = 'practice.availability'
    _description = 'Practice Availability'

    day_of_week = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], string="Day", required=True)

    start_time = fields.Float(
        string="Start Time",
        help="Start time for this day."
    )

    end_time = fields.Float(
        string="End Time",
        help="End time for this day."
    )

    practice_request_id = fields.Many2one(
        'practice.request',
        string="Practice Request",
        required=True
    )
