# -*- coding: utf-8 -*-
{
    'name': 'Isep form card link',
    'version': '16.1',
    'summary': """ Módulo que envía link de tarjeta para el registro, mediante correo electrónico en periodos mensuales """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': 'Sale',
    'depends': ['base', 'sale', 'isep_form_data', 'account' ],
    "data": [
        "views/res_config_settings_views.xml",
        "data/cron_action.xml",
        "data/mail_template.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
