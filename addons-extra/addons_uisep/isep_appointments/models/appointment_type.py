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

class AppointmentType(models.Model):
    _inherit = "appointment.type"

    is_private_appo = fields.Boolean('Private Appointment?', help="Only internal users can view this appointment in website")