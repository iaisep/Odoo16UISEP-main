# -*- coding: utf-8 -*---

{
    'name': 'Isep - Pricelist Custom',
    'version': '1.0',
    'category': 'Sales',
    'license':'AGPL-3',
    'summary': 'Pricelist Custom',
    'description': """
        Pricelist Custom.
    """,
    'depends': ['sale_temporal'],
    'author' : 'HFoc',
    'data': [
        'views/product_pricelist.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
