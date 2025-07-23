# -*- coding: utf-8 -*-
{
    'name': 'Isep Group Private Phone/Móvil',
    'version': '16.1',
    'summary': """ Modulo que oculta los numeros de teléfono y móvil del res.partner """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': ['base', ],
    "data": [
        "views/res_partner_views.xml",
        "security/group.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
