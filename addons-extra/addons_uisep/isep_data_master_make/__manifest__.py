# -*- coding: utf-8 -*-
{
    'name': 'Isep Data Make',
    'version': '16.1',
    'summary': """  Módulo que registra los datos para Make """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': ['base', 'openeducat_core', 'openeducat_admission'],
    "data": [
        "security/ir.model.access.csv",
        "views/data_master_make_views.xml",
        "views/op_admission_views.xml",
        "views/op_batch_views.xml",
        "data/cron_data_make.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
