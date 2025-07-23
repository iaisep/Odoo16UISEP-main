# -*- coding: utf-8 -*-
{
    'name': 'Ecommerce Fix',
    'version': '16.1',
    'summary': """ Modulo que hereda de isep_openeducat_sale y  isep_website_sale_custom, agrega condicionante al producto en el ecommerce""",
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': ['base', 'isep_openeducat_sale', 'isep_website_sale_custom'],
    "data": [
        "views/product_template_views.xml",
        "views/template_extra_info.xml",
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
