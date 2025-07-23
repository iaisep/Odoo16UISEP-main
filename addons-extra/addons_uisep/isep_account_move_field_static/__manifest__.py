# -*- coding: utf-8 -*-
{
    'name': 'Isep Account Move Field Static',
    'version': '16.1',
    'summary': """ Modulo   que agrega campos estáticos de telefono y correo en la factura """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': 'account',
    'depends': ['base', 'account'],
    "data": [
        "views/account_move_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
