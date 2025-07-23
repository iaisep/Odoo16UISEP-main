# -*- coding: utf-8 -*-
{
    'name': 'Isep Subscription Cron Invoices',
    'version': '16.1',
    'description': """ Módulo para crear con dias anticipados a la fecha de facturacion """,
    'summary': """ Módulo para crear con dias anticipados a la fecha de facturacion """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': [
        'base', 
        'sale',
        'payment',
        'account',
        'account_edi',
        'sms',
        'sale_subscription' ],
    "data": [
        "views/payment_provider_views.xml",
        "views/account_move_views.xml",
        "data/cron_sale_order_link_payment.xml",
        "data/mail_template.xml",
        "views/res_config_settings_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
