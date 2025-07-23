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
{
    'name': 'ISEP Website Appointments - Changes',
    'version': '16.0.0',
    'summary': 'Website Appointment History and Cancel',
    'description': 'Managed Appointments to cancel, see history and penalize students',
    'category': 'Tools',
    'author': 'ABL Solutions',
    'license': 'Other proprietary',
    'support':'infoablsolutions24@gmail.com',
    'depends': ['website_appointment','openeducat_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/ir_cron.xml',
        'views/appointment_type.xml',
        'views/appointment_penalization.xml',
        'views/calendar_event.xml',
        'views/res_config_settings.xml',
        'views/templates.xml'
    ],
    'installable': True,
    'auto_install': False,
}