# -*- coding: utf-8 -*-
{
    'name': 'Import Csv para Conciliar Facturas y Estractos Bancarios',
    'version': '16.1',
    'summary': """ Modulo que permite realizar las conciliaciones bancarias """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': 'Account',
    'depends': ['base','account' ],
    "data": [
        "wizard/reconcile_wizard.xml",
        "security/ir.model.access.csv"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
