# -*- coding: utf-8 -*-
{
    'name': "Isep - Formulario Portal tarjetas",
    'summary': """
        Módulo para el registro de la tarjeta del cliente desde el  portal 
    """,
    'description': """
        Módulo para el registro de la tarjeta del cliente desde el  portal
    """,
    'author': "Breithner Aquituari",
    'category': 'Sale',
    'version': '0.1',
    'depends': [
        'base',
        'sale',
        ],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/website_form.xml',
        'wizard/form_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/isep_form_data/static/src/scss/form.scss',
        ],
    }
}
