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

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    isp_time_before_reunion  = fields.Integer('Time Before Reunion',
        config_parameter="isep_appointments.isp_time_before_reunion",
        help="Time to show link reunion in minutes, before the time start.",
        default=15,
        readonly=False,
    )

    isp_time_after_reunion = fields.Integer('Time After Reunion',
                                           config_parameter="isep_appointments.isp_time_after_reunion",
                                           help="Time to show link reunion in minutes, after the time start.",
                                           default=15,
                                           readonly=False,
                                           )