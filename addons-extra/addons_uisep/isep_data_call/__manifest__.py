# -*- coding: utf-8 -*-
{
    'name': 'Isep Data Call',
    'version': '16.1',
    'summary': """ Módulo que registra datos del servicio de asistencia """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': ['base', 'openeducat_core', 'connect_chatgpt'],
    "data": [
        "views/data_master_call_views.xml",
        "security/ir.model.access.csv",
        "data/cron_data_call.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
