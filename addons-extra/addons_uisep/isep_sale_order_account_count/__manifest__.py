# -*- coding: utf-8 -*-
{
    'name': 'Isep Modulos de facturas vencidas',
    'version': '16.1',
    'summary': """ Modulo que hace el conteo de facturas vencidas """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': ['base', 'sale'],
    "data": [
        "views/sale_order_views.xml",
        "data/sale_order_cron.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
