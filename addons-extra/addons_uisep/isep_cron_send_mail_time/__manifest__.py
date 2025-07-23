# -*- coding: utf-8 -*-
{
    'name': 'Isep Cron Send Mail Massive for Time',
    'version': '16.1',
    'summary': """ Modulo que envia correos masivos con el link de pago como recordatorios """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': [
        'base', 
        'account', 
        'isep_sale_order_cron_payment' ],
    "data": [
        "data/cron_sale_order_link.xml",
        "views/res_config_settings_views.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
