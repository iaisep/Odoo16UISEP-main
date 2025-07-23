# -*- coding: utf-8 -*-
#################################################################################
# Author      : ISEP
# Copyright(c): 2016-Present .
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#################################################################################
from odoo import api, fields, models

class AppointmentPenalization(models.Model):
    _name="appointment.penalization"
    _description = "Appointment Penalization"

    name = fields.Char('Name Penalization',required=True)
    qty_absence = fields.Integer('Amount of Absenteeism',required=True)
    qty_days = fields.Integer('QTY Days', help="Number of Days to allow scheduling a new appointment")

class AppointmentPenalizationLine(models.Model):
    _name="appointment.penalization.line"
    _description = "Appointment Penalization Line"

    datetime_create = fields.Datetime('Date Penalization',required=True)
    user_id = fields.Many2one('res.users','Users',required=True)
    penalization_id = fields.Many2one('appointment.penalization','Penalization ID',required=False)
    next_date_book = fields.Datetime('Next date to schedule',required=False)
    total_absence = fields.Integer('Total Absence',default=0)
