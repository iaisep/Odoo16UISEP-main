# -*- coding: utf-8 -*-
{
    'name': "Isep - Sign Sale",
    'summary': """
        Módulo para enviar a firmar
    """,
    'description': """
        Módulo para enviar a firmar
    """,
    'author': "Breithner Aquituari - Hans Olivos",
    'category': 'Sale',
    'version': '0.1',
    'depends': [
        'base',
        'sale',
        'sign',
        'isep_form_data',
        'l10n_latam_base',
        'sale_subscription',
        ],
    'data': [
        'views/sale_order_view.xml',
        'views/sign_template_view.xml',
        'views/res_partner_view.xml',    
        'views/res_company.xml',        
        'report/sheet_prematricula_isep.xml',
        'report/sheet_prematricula_isep_br.xml',
    ],
}
